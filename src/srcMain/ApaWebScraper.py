from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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
from utils.utils import *
from utils.asl import *
from src.dataClasses.SessionSeason import SessionSeason


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
            options.add_argument('--headless=new')
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
        time.sleep(2)
        noThanksButton = self.driver.find_element(By.XPATH, "//a[text()='No Thanks']")
        noThanksButton.click()

    ############### Scraping Data for Division/Session ###############
    def scrapeDivision(self, divisionId):
        self.createWebDriver()
        print(f"Fetching results for division {divisionId}")
        self.driver.get(f"{self.config.get('apaWebsite').get('divisionBaseLink')}{divisionId}")
        time.sleep(1)
        division = self.addDivisionToDatabase()
        table = self.driver.find_element(By.TAG_NAME, "tbody")
        divisionId = division.getDivisionId()
        teamLinks = []
        for row in table.find_elements(By.TAG_NAME, "tr"):
            teamLinks.append(self.config.get('apaWebsite').get('baseLink') + row.get_attribute("to"))
        
        argsList = ((division, teamLink, divisionId) for teamLink in teamLinks)
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.scrapeTeamInfoAndTeamMatches, argsList) 
        print("finished first mapping")
        if self.config.get('debugMode'):
            for args in self.db.getTeamMatches(divisionId):
                self.transformScrapeMatchLinksAllTeams(args)
        else:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.transformScrapeMatchLinksAllTeams, self.db.getTeamMatches(divisionId))

        # Now set all the adjusted skills
        playerMatches = list(map(lambda playerMatch: self.converter.toPlayerMatchWithSql(playerMatch), self.db.getPlayerMatches(None, divisionId, None, None, None, None, None, None, None, None)))
       
        for playerMatch in playerMatches:
            for index, playerResult in enumerate(playerMatch.getPlayerResults()):
                self.db.updateASL(
                    playerMatch.getPlayerMatchId(),
                    playerMatch.getTeamMatchId(),
                    getAdjustedSkillLevel(playerResult.getPlayer().getMemberId(), playerResult.getSkillLevel(), playerMatch.getDatePlayed(), playerMatch.getPlayerMatchId()),
                    index
                )
            

        end = time.time()
        
        length = end - start
        print(f"scraping time: {length} seconds")

    def scrapeTeamInfoAndTeamMatches(self, args):
        apaWebScraperWorker = ApaWebScraperWorker()
        apaWebScraperWorker.scrapeTeamInfoAndTeamMatches(args)
    
    def transformScrapeMatchLinksAllTeams(self, args):
        apaWebScraperWorker = ApaWebScraperWorker()
        apaWebScraperWorker.scrapePlayerMatches(args)

    def scrapeDivisionsForSession(self, sessionId):
        self.createWebDriver()
        self.driver.get(f"{self.config.get('apaWebsite').get('sessionBaseLink')}{sessionId}")
        time.sleep(4)
        div = self.driver.find_element(By.CLASS_NAME, "m-b-30")
        aTags = div.find_elements(By.TAG_NAME, "a")
        divisionLinks = list(map(lambda aTag: aTag.get_attribute('href'), aTags))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.transformScrapeDivisionsForSession, divisionLinks)
    
    def transformScrapeDivisionsForSession(self, divisionLink):
        apaWebScraperWorker = ApaWebScraperWorker()
        apaWebScraperWorker.scrapeDivisionForSession(divisionLink)


    ############### Adding Values to Database ###############    
    def addDivisionToDatabase(self):
        # Check if division/session already exists in the database
        divisionName = ' '.join(self.driver.find_element(By.CLASS_NAME, 'page-title').text.split(' ')[:-1])
        divisionId = removeElements(self.driver.current_url.split('/'), ["standings"])[-1]
        sessionElement = self.driver.find_element(By.CLASS_NAME, "m-b-10")
        sessionSeason, sessionYear = sessionElement.text.split(' ')
        sessionId = sessionElement.find_elements(By.TAG_NAME, "a")[0].get_attribute('href').split('/')[-1]
        division = self.converter.toDivisionWithSql(self.db.getDivision(divisionId))
        if division is not None:
            return division
        
        # Division/session doesn't exist in the database, so scrape all necessary values
        
        formatElement = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Format:')]")[0]
        game = formatElement.find_elements(By.XPATH, "..")[0].text.split(' ')[1].lower()
        dayTimeElement = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Day/Time:')]")[0]
        day = dayTimeElement.find_elements(By.XPATH, "..")[0].text.split(' ')[1].lower()
        dayOfWeek = time.strptime(day, "%A").tm_wday

        # Add division/sesion to database
        division = self.converter.toDivisionWithDirectValues(sessionId, SessionSeason[sessionSeason], sessionYear, divisionId, divisionName, dayOfWeek, game)
        self.db.addDivision(division)
        return division
    
    ############### Finding Next Opponents ###############   
    def getOpponentTeam(self, teamId):
        # Go to division link
        # Find and click on your team name
        # Go down their schedule and get the team name for the next match that hasn't been played
        self.createWebDriver()
        self.driver.get(f"{self.config.get('apaWebsite').get('teamBaseLink')}{teamId}")
        teamNum = int(self.db.getTeamNum(teamId))

        headerTexts = ['Team Schedule & Results', 'Playoffs']
        for headerText in headerTexts:
            header = self.driver.find_element(By.XPATH, f"//h2 [contains( text(), '{headerText}')]")
            matches = header.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "a")
            for match in matches:
                if '@' in match.text:
                    'WEEK 5\nFeb\n29\nThursday\nPool Gods(24505)\nSir-Scratch-A Lot(24504)\nCity Pool Hall @ 7:00 pm'
                    textElements = match.text.split('\n')

                    teamNum1 = int(re.sub(r'\W+', '', removeElements(textElements[4].split('(')[1], [")"])[-2:]))
                    teamNum2 = int(re.sub(r'\W+', '', removeElements(textElements[5].split('(')[1], [")"])[-2:]))
                    opponentTeamNum = None
                    if teamNum1 == teamNum:
                        opponentTeamNum = teamNum2
                    else:
                        opponentTeamNum = teamNum1
                    
                    return self.converter.toTeamWithSql(self.db.getTeamWithTeamNum(opponentTeamNum, self.db.getDivisionIdFromTeamId(teamId)))
                
    def scrapeAllEightBallThursDivisions(self):
        self.createWebDriver()
        
        
        for sessionId in range(89, 131):
            self.scrapeDivisionsForSession(sessionId)
            
            self.driver.get(f"{self.config.get('apaWebsite').get('sessionBaseLink')}{sessionId}")
            time.sleep(4)
            div = self.driver.find_element(By.CLASS_NAME, "m-b-30")
            aTags = div.find_elements(By.TAG_NAME, "a")
            for tag in aTags:
                if "245" in tag.text:
                    divisionId = int(tag.get_attribute('href').split('/')[-1])
                    self.scrapeDivision(divisionId)
                    break

                

                    
        
                    