from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataClasses.Player import Player
from dataClasses.Team import Team
from converter.Converter import Converter
from src.srcMain.Database import Database
from src.srcMain.Config import Config
import calendar
import re
from dataClasses.PlayerResult import PlayerResult
from dataClasses.Score import Score
from dataClasses.Team import Team
from src.srcMain.Database import Database
from dataClasses.Player import Player
from dataClasses.PlayerMatch import PlayerMatch
from dataClasses.Division import Division
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.utils import *
from utils.asl import *
from dataClasses.Team import Team
from src.dataClasses.Format import Format
from src.dataClasses.SessionSeason import SessionSeason
from src.srcMain.Typechecked import Typechecked
from typing import Tuple


class ApaWebScraperWorker(Typechecked):
    ############### Startup ###############
    def __init__(self):
        self.config = Config().getConfig()
        self.converter = Converter()
        self.driver = None
        self.db = Database()
    
    def createWebDriver(self) -> None:
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
    
    def login(self) -> None:
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
        time.sleep(2)
        noThanksButton = self.driver.find_element(By.XPATH, "//a[text()='No Thanks']")
        noThanksButton.click()


    ############### Team Scraping Functions ###############
    def scrapeTeamInfo(self, division: Division) -> Team:
        teamId = self.driver.current_url.split('/')[-1]
        time.sleep(1)
        data = self.driver.find_element(By.CLASS_NAME, 'page-title').text.split('\n')
        teamName = data[0]
        teamNum = int(re.sub(r'\W+', '', data[1]))

        roster = self.getRoster()

        return Team(division, teamId, teamNum, teamName, roster)
    
    def getRoster(self) -> List[Player]:
        self.createWebDriver()
        time.sleep(1)
        rows = self.driver.find_element(By.XPATH, "//h2 [contains( text(), 'Team Roster')]").find_element(By.XPATH, "..").find_elements(By.TAG_NAME, 'table')[0].find_elements(By.TAG_NAME, "tr")
        roster = []
        for row in rows[1:]:
            data = row.text.split('\n')
            playerName = data[0].replace('"', "'")
            memberId = int(re.sub(r'\W+', '', data[1]))
            currentSkillLevel = data[2][0]
            if currentSkillLevel == "-":
                currentSkillLevel = DEFAULT_SKILL_LEVEL
            else:
                currentSkillLevel = int(currentSkillLevel)
            roster.append(Player(memberId, playerName, currentSkillLevel))
        return roster
    
    def scrapeTeamInfoAndTeamMatches(self, args: Tuple[Division, str, int]) -> None:
        division, teamLink, divisionId = args
        self.driver = None
        self.createWebDriver()
        self.driver.get(teamLink)
        teamInfo = self.scrapeTeamInfo(division)
        self.db.addTeamInfo(teamInfo)

        matchLinks = self.scrapeTeamMatchesForTeam('Team Schedule & Results', divisionId)
        matchLinks = matchLinks + self.scrapeTeamMatchesForTeam('Playoffs', divisionId)
        print("Got team data")

    def scrapeTeamMatchesForTeam(self, headerTitle: str, divisionId: int) -> List[str]:
        self.createWebDriver()
        
        matchesHeader = self.driver.find_element(By.XPATH, "//h2 [contains( text(), '{}')]".format(headerTitle))
        matches = matchesHeader.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "a")
        
        matchLinks = []
        for match in matches:
            if '|' in match.text:
                link = match.get_attribute("href")
                teamMatchId = link.split("/")[-1]
                apaDatetime = self.apaDateToDatetime(match.text.split(' | ')[-1])
                if not self.db.isValueInTeamMatchTable(teamMatchId):
                    matchLinks.append(link)
                    self.db.addTeamMatch(teamMatchId, apaDatetime, divisionId)
                
        return matchLinks
    
    def apaDateToDatetime(self, apaDate: str) -> str:
        apaDate = apaDate.replace(',', '')
        month, day, year = apaDate.split(' ')
        return "{}-{}-{}".format(year, str(list(calendar.month_abbr).index(month)).zfill(2), day)
    

    ############### PlayerMatch Scraping Functions ###############
    def scrapePlayerMatches(self, args: Tuple[int, int]) -> None:
        teamMatchId, divisionId = args
        teamMatchLink = self.config.get('apaWebsite').get('teamMatchBaseLink') + str(teamMatchId)
        self.createWebDriver()
        playerMatches = self.getPlayerMatchesFromTeamMatch(teamMatchLink, divisionId)
        for match in playerMatches:
            self.db.addPlayerMatch(match)
        print("Total player matches in database = {}".format(str(self.db.countPlayerMatches())))

    def getPlayerMatchesFromTeamMatch(self, link: str, divisionId: int) -> List[PlayerMatch]:
        format = self.db.getFormat(divisionId)
        
        self.createWebDriver()
        self.driver.get(link)

        if format == Format.EIGHT_BALL:
            time.sleep(9)

        teamsInfoHeader = self.driver.find_elements(By.CLASS_NAME, "teamName")
        teamNum1 = int(re.sub(r'\W+', '', teamsInfoHeader[0].text.split(' (')[1])[-2:])
        
        team1 = self.converter.toTeamWithSql(self.db.getTeamWithTeamNum(teamNum1, divisionId))
        if not team1:
            return []
        teamNum2 = int(re.sub(r'\W+', '', teamsInfoHeader[1].text.split(' (')[1])[-2:])
        team2 = self.converter.toTeamWithSql(self.db.getTeamWithTeamNum(teamNum2, divisionId))
        if not team2:
            return []

        matchesHeader = self.driver.find_element(By.XPATH, "//h3 [contains( text(), 'MATCH BREAKOUT')]")
        matchesDiv = matchesHeader.find_element(By.XPATH, "..")
        if not self.waitFor(15, self.areSkillLevelsLoaded, matchesDiv):
            print("ERROR: skill levels never loaded")
            exit(1)
        
        individualMatches = matchesDiv.find_elements(By.XPATH, "./*")
        
        playerMatches = []
        playerMatchId = 0
        teamMatchId = link.split('/')[-1]
        datePlayed = self.db.getDatePlayed(teamMatchId)
        for individualMatch in individualMatches:
            if 'LAG' not in individualMatch.text:
                continue
            playerMatchId += 1
            mapper = None
            if format == Format.NINE_BALL:
                mapper = nineBallSkillLevelMapper()
            
            textElements = individualMatch.text.split('\n')

            removableWordList = ['LAG', 'SL', 'Pts Earned']
            if format == Format.EIGHT_BALL:
                removableWordList.append('GW/GMW')
            elif format == Format.NINE_BALL:
                removableWordList.append('PE/PN')
            textElements = removeElements(textElements, removableWordList)
            
            playerName1 = textElements[0].replace('"', "'")
            playerName2 = textElements[6].replace('"', "'")
            skillLevel1 = int(textElements[1])
            skillLevel2 = int(textElements[5])
            if format == Format.EIGHT_BALL and EIGHT_BALL_INCORRECT_SKILL_LEVEL in [skillLevel1, skillLevel2]:
                print("ERROR: scraped skill level incorrectly")
                exit(1)
            if format == Format.NINE_BALL.value:
                skillLevel1 = mapper.get(playerPtsNeeded1)
            teamPtsEarned1 = int(textElements[2])
            teamPtsEarned2 = int(textElements[7])

            score = textElements[4]
            scoreElements = score.split(' - ')
            score1 = list(map(lambda pointAmount: int(pointAmount), scoreElements[0].split('/')))
            score2 = list(map(lambda pointAmount: int(pointAmount), scoreElements[1].split('/')))
            if len(score1) == 1 or len(score2) == 1:
                if format == Format.EIGHT_BALL:
                    isFirstResultOfNewPlayer = skillLevel1 == NEW_PLAYER_SCRAPED_SKILL_LEVEL
                    oldPlayerSkillLevel = skillLevel2 if isFirstResultOfNewPlayer else skillLevel1
                    newPlayerTeamPtsEarned = teamPtsEarned1 if isFirstResultOfNewPlayer else teamPtsEarned2
                    oldPlayerTeamPtsEarned = teamPtsEarned2 if isFirstResultOfNewPlayer else teamPtsEarned1
                    newPlayerScore, oldPlayerScore = eightBallNewPlayerMapper(oldPlayerSkillLevel, newPlayerTeamPtsEarned, oldPlayerTeamPtsEarned)
                    score1 = newPlayerScore if isFirstResultOfNewPlayer else oldPlayerScore
                    score2 = oldPlayerScore if isFirstResultOfNewPlayer else newPlayerScore
                else:
                    score1.insert(0, 0)
                    score2.insert(0, 0)
            
            if skillLevel1 == NEW_PLAYER_SCRAPED_SKILL_LEVEL:
                skillLevel1 = DEFAULT_SKILL_LEVEL
            if skillLevel2 == NEW_PLAYER_SCRAPED_SKILL_LEVEL:
                skillLevel2 = DEFAULT_SKILL_LEVEL

            playerPtsEarned1, playerPtsNeeded1 = score1
            
            playerPtsEarned2, playerPtsNeeded2 = score2
            
            if format == Format.NINE_BALL:
                skillLevel2 = mapper.get(playerPtsNeeded2)
            
            

            db = Database()
            
            score1 = Score(teamPtsEarned1, playerPtsEarned1, playerPtsNeeded1)
            score2 = Score(teamPtsEarned2, playerPtsEarned2, playerPtsNeeded2)

            playerResults = []
            
            # TODO: Figure out how to find the memberId/currentSkillLevel of a player who once belonged to a team but no longer does
            player1Info = db.getPlayerBasedOnTeamIdAndPlayerName(team1.getTeamId(), playerName1)
            if player1Info is None:
                # TODO: Figure out if there's another way to get player info for a player who isn't on a team anymore
                continue
            memberId1, playerName1, currentSkillLevel1 = player1Info
            player1 = Player(memberId1, playerName1, currentSkillLevel1)
            
            player2Info = db.getPlayerBasedOnTeamIdAndPlayerName(team2.getTeamId(), playerName2)
            if player2Info is None:
                # TODO: Figure out if there's another way to get player info for a player who isn't on a team anymore
                continue
            memberId2, playerName2, currentSkillLevel2 = player2Info
            player2 = Player(memberId2, playerName2, currentSkillLevel2)

            playerResults.append(PlayerResult(team1, player1, skillLevel1, score1, None))
            playerResults.append(PlayerResult(team2, player2, skillLevel2, score2, None))
            playerMatch = PlayerMatch(playerResults, playerMatchId, teamMatchId, datePlayed)

            if playerMatch is not None:
                playerMatches.append(playerMatch)   
        
        return playerMatches
    
    def scrapeDivisionForSession(self, divisionLink: str) -> None:
        self.createWebDriver()
        self.driver.get(divisionLink)
        time.sleep(1)
        # Check if division/session already exists in the database
        divisionName = ' '.join(self.driver.find_element(By.CLASS_NAME, 'page-title').text.split(' ')[:-1])
        divisionId = removeElements(self.driver.current_url.split('/'), ["standings"])[-1]
        sessionElement = self.driver.find_element(By.CLASS_NAME, "m-b-10")
        sessionSeason, sessionYear = sessionElement.text.split(' ')
        sessionId = sessionElement.find_elements(By.TAG_NAME, "a")[0].get_attribute('href').split('/')[-1]
        
        # Division/session doesn't exist in the database, so scrape all necessary values
        formatElement = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Format:')]")[0]
        format = formatElement.find_elements(By.XPATH, "..")[0].text.split(' ')[1].lower()
        dayTimeElement = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Day/Time:')]")[0]
        day = dayTimeElement.find_elements(By.XPATH, "..")[0].text.split(' ')[1].lower()
        dayOfWeek = time.strptime(day, "%A").tm_wday

        # Add division/sesion to database
        division = self.converter.toDivisionWithDirectValues(sessionId, SessionSeason[sessionSeason], sessionYear, divisionId, divisionName, dayOfWeek, Format(format))
        self.db.addDivision(division)

        
    def areSkillLevelsLoaded(self, matchesDiv) -> bool:
        individualMatches = matchesDiv.find_elements(By.XPATH, "./*")
        for individualMatch in individualMatches:
            if 'LAG' not in individualMatch.text:
                continue
        
            textElements = individualMatch.text.split('\n')

            removableWordList = ['LAG', 'SL', 'Pts Earned']
            removableWordList.append('GW/GMW')
            textElements = removeElements(textElements, removableWordList)
            skillLevel1 = int(textElements[1])
            skillLevel2 = int(textElements[5])
            return EIGHT_BALL_INCORRECT_SKILL_LEVEL not in [skillLevel1, skillLevel2]
        return False
    
    def waitFor(self, seconds: int, function, param) -> bool:
        while seconds > 0:
            if function(param):
                return True
            else:
                time.sleep(0.5)
                seconds -= 0.5
        return False