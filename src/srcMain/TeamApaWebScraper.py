from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataClasses.nineBall.NineBallPlayerMatch import NineBallPlayerMatch
from dataClasses.eightBall.EightBallPlayerMatch import EightBallPlayerMatch
from dataClasses.Division import Division
from dataClasses.Session import Session
from dataClasses.Player import Player
from dataClasses.Team import Team
from converter.Converter import Converter
from src.srcMain.Database import Database
from src.srcMain.Config import Config
import calendar
import re
import concurrent.futures


class TeamApaWebScraper:
    #### Startup ####
    def __init__(self):
        self.config = Config().getConfig()
        self.converter = Converter()
        self.driver = None
        self.db = Database()
    
    def createWebDriver(self):
        if self.driver is not None:
            return
        driver = webdriver.Chrome()
        if not self.config.get('debugMode'):
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        self.driver = driver
        self.login()
    
    def login(self):
        # Go to signin page
        self.driver.get(self.config.get('apaWebsite').get('loginLink'))

        # Login
        APA_EMAIL = os.environ['APA_EMAIL']
        APA_PASSWORD = os.environ['APA_PASSWORD']
        usernameElement = self.driver.find_element(By.ID, 'email')
        usernameElement.send_keys(APA_EMAIL)
        passwordElement = self.driver.find_element(By.ID, 'password')
        passwordElement.send_keys(APA_PASSWORD)
        passwordElement.send_keys(Keys.ENTER)
        time.sleep(self.config.get('waitTimes').get('sleepTime'))
        continueLink = self.driver.find_element(By.XPATH, "//button[text()='Continue']")
        print("found continue link")
        continueLink.click()
        time.sleep(5)
        noThanksButton = self.driver.find_element(By.XPATH, "//a[text()='No Thanks']")
        noThanksButton.click()


    def scrapeTeamInfo(self, division):
        teamId = self.driver.current_url.split('/')[-1]
        time.sleep(1)
        data = self.driver.find_element(By.CLASS_NAME, 'page-title').text.split('\n')
        teamName = data[0]
        teamNum = int(re.sub(r'\W+', '', data[1]))

        roster = self.getRoster()

        return Team(division, teamId, teamNum, teamName, roster)
    
    def getRoster(self):
        self.createWebDriver()
        rows = self.driver.find_element(By.XPATH, "//h2 [contains( text(), 'Team Roster')]").find_element(By.XPATH, "..").find_elements(By.TAG_NAME, 'table')[0].find_elements(By.TAG_NAME, "tr")
        roster = []
        for row in rows[1:]:
            data = row.text.split('\n')
            playerName = data[0]
            memberId = int(re.sub(r'\W+', '', data[1]))
            currentSkillLevel = data[2][0]
            roster.append(Player(memberId, playerName, currentSkillLevel))
        return roster
    
    def transformScrapeDivision(self, args):
        division, teamLink, divisionId, sessionId, isEightBall = args
        self.driver = None
        self.createWebDriver()
        self.driver.get(teamLink)
        teamInfo = self.scrapeTeamInfo(division)
        self.db.addTeamInfo(teamInfo)

        matchLinks = self.scrapeTeamMatchesForTeam('Team Schedule & Results', divisionId, sessionId, isEightBall)
        print("finished 1 matchlinks")
        matchLinks = matchLinks + self.scrapeTeamMatchesForTeam('Playoffs', divisionId, sessionId, isEightBall)
        print("finished 2 matchlinks")
        print("Got team data")

    def scrapeTeamMatchesForTeam(self, headerTitle, divisionId, sessionId, isEightBall):
        self.createWebDriver()
        
        matchesHeader = self.driver.find_element(By.XPATH, "//h2 [contains( text(), '{}')]".format(headerTitle))
        matches = matchesHeader.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "a")
        
        matchLinks = []
        for match in matches:
            if '|' in match.text:
                link = match.get_attribute("href")
                teamMatchId = link.split("/")[-1]
                apaDatetime = self.apaDateToDatetime(match.text.split(' | ')[-1])
                if not self.db.isValueInTeamMatchTable(teamMatchId, isEightBall):
                    matchLinks.append(link)
                    self.db.addTeamMatchValue(teamMatchId, apaDatetime, divisionId, sessionId, isEightBall)
                
        return matchLinks
    
    def apaDateToDatetime(self, apaDate):
        apaDate = apaDate.replace(',', '')
        month, day, year = apaDate.split(' ')
        return "{}-{}-{}".format(year, str(list(calendar.month_abbr).index(month)).zfill(2), day)
    
    def transformScrapeMatchLinks(self, args):
        teamMatchId, divisionId, sessionId, game = args
        teamMatchLink = self.config.get('apaWebsite').get('teamMatchBaseLink') + str(teamMatchId)
        isEightBall = game == "8-ball"
        self.createWebDriver()
        for match in self.getPlayerMatchesFromTeamMatch(teamMatchLink, divisionId, sessionId, isEightBall):
            self.db.addPlayerMatch(match, isEightBall)
        print("Total player matches in database = {}".format(str(self.db.countPlayerMatches(isEightBall))))

    def getPlayerMatchesFromTeamMatch(self, link, divisionId, sessionId, isEightBall):
        self.createWebDriver()
        self.driver.get(link)
        if isEightBall:
            time.sleep(10)

        teamsInfoHeader = self.driver.find_elements(By.CLASS_NAME, "teamName")
        teamName1 = teamsInfoHeader[0].text.split(' (')[0]
        teamNum1 = int(re.sub(r'\W+', '', teamsInfoHeader[0].text.split(' (')[1])[-2:])
        
        #TODO: find out if you can use a converter here to transform the sql values into a team object. There might be a circular dependency
        
        team1 = self.converter.toTeamWithSql(self.db.getTeam(teamName1, teamNum1, divisionId, sessionId))
        teamName2 = teamsInfoHeader[1].text.split(' (')[0]
        teamNum2 = int(re.sub(r'\W+', '', teamsInfoHeader[1].text.split(' (')[1])[-2:])
        team2 = self.converter.toTeamWithSql(self.db.getTeam(teamName2, teamNum2, divisionId, sessionId))


        matchesHeader = self.driver.find_element(By.XPATH, "//h3 [contains( text(), 'MATCH BREAKOUT')]")
        matchesDiv = matchesHeader.find_element(By.XPATH, "..")
        individualMatches = matchesDiv.find_elements(By.XPATH, "./*")
        
        playerMatches = []
        playerMatchId = 0
        teamMatchId = link.split('/')[-1]
        datePlayed = self.db.getDatePlayed(teamMatchId, isEightBall)
        for individualMatch in individualMatches:
            if 'LAG' not in individualMatch.text:
                continue
            playerMatchId += 1
            playerMatch = self.converter.toPlayerMatchWithDiv(individualMatch, team1, team2, playerMatchId, teamMatchId, datePlayed, isEightBall)

            if playerMatch is not None and playerMatch.toJson().get('playerResults')[0].get('skillLevel') != 0 and playerMatch.toJson().get('playerResults')[1].get('skillLevel') != 0:
                playerMatches.append(playerMatch)
            
        
        return playerMatches