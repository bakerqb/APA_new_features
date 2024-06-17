from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from converter.Converter import Converter
from src.srcMain.Database import Database
from src.srcMain.Config import Config
from src.srcMain.ApaWebScraperWorker import ApaWebScraperWorker
import re
import concurrent.futures


class ApaWebScraper:
    ############### Start Up ###############
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

    ############### Scraping Data for Division/Session ###############
    def scrapeDivision(self, divisionLink, isEightBall):
        self.createWebDriver()
        print("Fetching results for session with link = {}".format(divisionLink))
        self.driver.get(divisionLink)
        time.sleep(2)
        division = self.addDivisionToDatabase()
        table = self.driver.find_element(By.TAG_NAME, "tbody")
        divisionId = division.toJson().get('divisionId')
        sessionId = division.toJson().get('session').get('sessionId')
        teamLinks = []
        for row in table.find_elements(By.TAG_NAME, "tr"):
            teamLinks.append(self.config.get('apaWebsite').get('baseLink') + row.get_attribute("to"))
        
<<<<<<< HEAD
        argsList = ((division, teamLink, divisionId, sessionId, isEightBall) for teamLink in teamLinks)
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.scrapeTeamInfoAndTeamMatches, argsList) 
        print("finished first mapping")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.transformScrapeMatchLinksAllTeams, self.db.getTeamMatches(sessionId, divisionId, isEightBall))
=======
        # TODO: go through all teams and add team info, and save the match links in the meantime
        # TODO: then loop through all the player matches with the team info in mind
        teamsInfo = {}
        for teamLink in teamLinks:
            self.driver.get(teamLink)
            teamInfo = self.scrapeTeamInfo(division)
            self.db.addTeamInfo(teamInfo)

            matchLinks = self.scrapeTeamMatchesForTeam('Team Schedule & Results', divisionId, sessionId, isEightBall)
            matchLinks = matchLinks + self.scrapeTeamMatchesForTeam('Playoffs', divisionId, sessionId, isEightBall)
            teamsInfo[teamLink] = matchLinks
            print(f"Scraped team info for team {len(teamsInfo.keys())}")

        for teamLink, matchLinks in teamsInfo.items():
            # print("Total team matches in database = {}".format(self.db.countTeamMatches(IsEightBall)))
            self.scrapeMatchLinks(matchLinks, divisionId, sessionId, isEightBall)

    def scrapeTeamInfo(self, division):
        teamId = self.driver.current_url.split('/')[-1]
        time.sleep(1)
        data = self.driver.find_element(By.CLASS_NAME, 'page-title').text.split('\n')
        teamName = data[0]
        teamNum = int(re.sub(r'\W+', '', data[1]))

        roster = self.getRoster()

        return Team(division, teamId, teamNum, teamName, roster)

>>>>>>> cbf0c96 (feat: add adjusted skill level)

        end = time.time()
        
        length = end - start
        print(f"scraping time: {length} seconds")

    def scrapeTeamInfoAndTeamMatches(self, args):
        apaWebScraperWorker = ApaWebScraperWorker()
        apaWebScraperWorker.scrapeTeamInfoAndTeamMatches(args)
    
    def transformScrapeMatchLinksAllTeams(self, args):
        apaWebScraperWorker = ApaWebScraperWorker()
        apaWebScraperWorker.scrapePlayerMatches(args)

    ############### Adding Values to Database ###############    
    def addDivisionToDatabase(self):
        # Check if division/session already exists in the database
        divisionName = ' '.join(self.driver.find_element(By.CLASS_NAME, 'page-title').text.split(' ')[:-1])
        divisionId = re.sub(r'\W+', '', self.driver.find_elements(By.XPATH, f"//option[contains(text(), '{divisionName}')]")[0].text.split('-')[-1])
        sessionElement = self.driver.find_element(By.CLASS_NAME, "m-b-10")
        sessionSeason, sessionYear = sessionElement.text.split(' ')
        sessionId = sessionElement.find_elements(By.TAG_NAME, "a")[0].get_attribute('href').split('/')[-1]
        division = self.converter.toDivisionWithSql(self.db.getDivision(divisionId, sessionId))
        if division is not None:
            return division
        
        # Division/session doesn't exist in the database, so scrape all necessary values
        
        formatElement = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Format:')]")[0]
        game = formatElement.find_elements(By.XPATH, "..")[0].text.split(' ')[1].lower()
        dayTimeElement = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Day/Time:')]")[0]
        day = dayTimeElement.find_elements(By.XPATH, "..")[0].text.split(' ')[1].lower()
        dayOfWeek = time.strptime(day, "%A").tm_wday
        divisionId = re.sub(r'\W+', '', self.driver.find_elements(By.XPATH, f"//option[contains(text(), '{divisionName}')]")[0].text.split('-')[-1])

        # Add division/sesion to database
        division = self.converter.toDivisionWithDirectValues(sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game)
        self.db.addDivision(division)
        return division
<<<<<<< HEAD
=======


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
                    self.db.addTeamMatch(teamMatchId, apaDatetime, divisionId, sessionId, isEightBall)
                
        return matchLinks
>>>>>>> cbf0c96 (feat: add adjusted skill level)
    
    ############### Finding Next Opponents ###############
    def navigateToTeamPage(self, division_link, team_name):
        self.createWebDriver()
        self.driver.get(division_link)
        table = self.driver.find_element(By.TAG_NAME, "tbody")
        
        for row in table.find_elements(By.TAG_NAME, "tr"):
            elements = row.find_elements(By.TAG_NAME, "td")
            textElement = elements[1].find_element(By.TAG_NAME, "h5")
            potentialTeamName = textElement.text
            if potentialTeamName == team_name:
                row.click()
                return
    
    def getOpponentTeamName(self, myTeamName, divisionLink):
        # Go to division link
        # Find and click on your team name
        # Go down their schedule and get the team name for the next match that hasn't been played
        self.createWebDriver()
        self.navigateToTeamPage(divisionLink, myTeamName)

        headerTexts = ['Team Schedule & Results', 'Playoffs']
        for headerText in headerTexts:
            header = self.driver.find_element(By.XPATH, "//h2 [contains( text(), '{}')]".format(headerText))
            matches = header.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "a")
            for match in matches:
                if '@' in match.text:
                    'WEEK 5\nFeb\n29\nThursday\nPool Gods(24505)\nSir-Scratch-A Lot(24504)\nCity Pool Hall @ 7:00 pm'
                    textElements = match.text.split('\n')
                    team1 = textElements[4].split('(')[0]
                    team2 = textElements[5].split('(')[0]
                    if team1 == myTeamName:
                        return team2
                    else:
                        return team1
                    