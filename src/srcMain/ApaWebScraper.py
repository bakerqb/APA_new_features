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


class ApaWebScraper:
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
        if not self.config.get('debug_mode'):
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        self.driver = driver
        self.login()
    
    def login(self):
        # Go to signin page
        self.driver.get(self.config.get('apa_website').get('login_link'))

        # Login
        APA_EMAIL = os.environ['APA_EMAIL']
        APA_PASSWORD = os.environ['APA_PASSWORD']
        username_element = self.driver.find_element(By.ID, 'email')
        username_element.send_keys(APA_EMAIL)
        password_element = self.driver.find_element(By.ID, 'password')
        password_element.send_keys(APA_PASSWORD)
        password_element.send_keys(Keys.ENTER)
        time.sleep(self.config.get('wait_times').get('sleep_time'))
        continue_link = self.driver.find_element(By.XPATH, "//button[text()='Continue']")
        print("found continue link")
        continue_link.click()
        time.sleep(5)
        no_thanks_button = self.driver.find_element(By.XPATH, "//a[text()='No Thanks']")
        no_thanks_button.click()

    # SessionId formatted as a 2 or 3 digit character
    def scrapeSessionLink(self, sessionId):
        self.createWebDriver()
        self.driver.get(self.config.get('apa_website').get('session_link') + str(sessionId))
        try:
            nine_ball_header = self.driver.find_element(By.XPATH, "//h4 [contains( text(), 'Mon 9-BALL Cph')]")
            a_tag = nine_ball_header.find_element(By.XPATH, "../../..")
            link = a_tag.get_attribute("href")
            
            self.db.addNineBallDivisionValue(link)
        except NoSuchElementException:
            print("Skipped session {}. No data.".format(str(sessionId)))
        
        return link
    
    
    def scrapeDivision(self, division_link, is_eight_ball):
        self.createWebDriver()
        print("Fetching results for session with link = {}".format(division_link))
        self.driver.get(division_link)
        time.sleep(2)
        division = self.addDivisionToDatabase()
        table = self.driver.find_element(By.TAG_NAME, "tbody")
        divisionId = division.toJson().get('divisionId')
        sessionId = division.toJson().get('session').get('sessionId')
        team_links = []
        for row in table.find_elements(By.TAG_NAME, "tr"):
            team_links.append(self.config.get('apa_website').get('base_link') + row.get_attribute("to"))
        
        # TODO: go through all teams and add team info, and save the match links in the meantime
        # TODO: then loop through all the player matches with the team info in mind
        teams_info = {}
        for team_link in team_links:
            self.driver.get(team_link)

            teamInfo = self.scrapeTeamInfo(division)

            self.db.addTeamInfo(teamInfo)

            match_links = self.scrapeTeamMatchesForTeam('Team Schedule & Results', divisionId, is_eight_ball)
            match_links = match_links + self.scrapeTeamMatchesForTeam('Playoffs', divisionId, is_eight_ball)
            teams_info[team_link] = match_links

        for team_link, match_links in teams_info.items():
            # print("Total team matches in database = {}".format(self.db.countTeamMatches(is_eight_ball)))
            self.getTeamMatchResults(match_links, divisionId, sessionId, is_eight_ball)

    def scrapeTeamInfo(self, division):
        teamId = self.driver.current_url.split('/')[-1]
        time.sleep(1)
        data = self.driver.find_element(By.CLASS_NAME, 'page-title').text.split('\n')
        teamName = data[0]
        teamNum = int(re.sub(r'\W+', '', data[1]))

        roster = self.getRoster()

        return Team(division, teamId, teamNum, teamName, roster)


        
    def addDivisionToDatabase(self):
        # Check if division/session already exists in the database
        divisionName = ' '.join(self.driver.find_element(By.CLASS_NAME, 'page-title').text.split(' ')[:-1])
        divisionId = re.sub(r'\W+', '', self.driver.find_elements(By.XPATH, f"//option[contains(text(), '{divisionName}')]")[0].text.split('-')[-1])
        division = self.converter.toDivisionWithSql(self.db.getDivision(divisionId))
        if division is not None:
            return division
        
        # Division/session doesn't exist in the database, so scrape all necessary values
        sessionElement = self.driver.find_element(By.CLASS_NAME, "m-b-10")
        sessionSeason, sessionYear = sessionElement.text.split(' ')
        sessionId = sessionElement.find_elements(By.TAG_NAME, "a")[0].get_attribute('href').split('/')[-1]
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


    def scrapeTeamMatchesForTeam(self, headerTitle, divisionId, isEightBall):
        self.createWebDriver()
        
        matches_header = self.driver.find_element(By.XPATH, "//h2 [contains( text(), '{}')]".format(headerTitle))
        matches = matches_header.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "a")
        
        match_links = []
        for match in matches:
            if '|' in match.text:
                link = match.get_attribute("href")
                teamMatchId = link.split("/")[-1]
                apa_datetime = self.apaDateToDatetime(match.text.split(' | ')[-1])
                if not self.db.isValueInTeamMatchTable(teamMatchId, isEightBall):
                    match_links.append(link)
                    self.db.addTeamMatchValue(teamMatchId, apa_datetime, divisionId, isEightBall)
                
        return match_links
    
    def apaDateToDatetime(self, apa_date):
        apa_date = apa_date.replace(',', '')
        month, day, year = apa_date.split(' ')
        return "{}-{}-{}".format(year, str(list(calendar.month_abbr).index(month)).zfill(2), day)
    
    def getTeamsInDivision(self):
        self.createWebDriver()
        self.driver.get(self.config.get('apa_website').get('division_link'))
        table = self.driver.find_element(By.TAG_NAME, "tbody")

        teams = []
        for row in table.find_elements(By.TAG_NAME, "tr"):
            elements = row.find_elements(By.TAG_NAME, "td")
            text_element = elements[1].find_element(By.TAG_NAME, "h5")
            teams.append(text_element.text)
        return teams

    def navigateToTeamPage(self, division_link, team_name):
        self.createWebDriver()
        self.driver.get(division_link)
        table = self.driver.find_element(By.TAG_NAME, "tbody")
        
        for row in table.find_elements(By.TAG_NAME, "tr"):
            elements = row.find_elements(By.TAG_NAME, "td")
            text_element = elements[1].find_element(By.TAG_NAME, "h5")
            potential_team_name = text_element.text
            if potential_team_name == team_name:
                row.click()
                return
    
    # Returns list of PlayerMatches from TeamMatch
    def getPlayerMatchesFromTeamMatch(self, link, divisionId, sessionId, is_eight_ball):
        self.createWebDriver()
        self.driver.get(link)
        if is_eight_ball:
            time.sleep(10)

        teams_info_header = self.driver.find_elements(By.CLASS_NAME, "teamName")
        team_name1 = teams_info_header[0].text.split(' (')[0]
        team_num1 = int(re.sub(r'\W+', '', teams_info_header[0].text.split(' (')[1])[-2:])
        
        #TODO: find out if you can use a converter here to transform the sql values into a team object. There might be a circular dependency
        #Example: team1 = self.converter.toTeamWithSql(self.db.getTeam(team_name1, team_num1, divisionId, sessionId))
        team1 = self.db.getTeam(team_name1, team_num1, divisionId, sessionId)
        team_name2 = teams_info_header[1].text.split(' (')[0]
        team_num2 = int(re.sub(r'\W+', '', teams_info_header[1].text.split(' (')[1])[-2:])
        team2 = self.db.getTeam(team_name2, team_num2, divisionId, sessionId)


        matches_header = self.driver.find_element(By.XPATH, "//h3 [contains( text(), 'MATCH BREAKOUT')]")
        matches_div = matches_header.find_element(By.XPATH, "..")
        individual_matches = matches_div.find_elements(By.XPATH, "./*")
        
        player_matches = []
        player_match_id = 0
        team_match_id = link.split('/')[-1]
        date_played = self.db.getDatePlayed(team_match_id, is_eight_ball)
        for individual_match in individual_matches:
            if 'LAG' not in individual_match.text:
                continue
            player_match_id += 1
            player_match = self.converter.toPlayerMatchWithDiv(individual_match, team1, team2, player_match_id, team_match_id, date_played, is_eight_ball)

            if player_match.getPlayerMatchResult()[0].get_skill_level() is not None and player_match.getPlayerMatchResult()[1].get_skill_level() is not None:
                player_matches.append(player_match)
            
        
        return player_matches

    # Loops through all TeamMatches from team
    # Gets all PlayerMatches for entire session
    # Adds PlayerMatches to database
    def getTeamMatchResults(self, match_links, divisionId, sessionId, is_eight_ball):
        matches = []
        for match_link in match_links:
            for match in self.getPlayerMatchesFromTeamMatch(match_link, divisionId, sessionId, is_eight_ball):
                self.db.addPlayerMatchValue(match, is_eight_ball)
        
        print("Total player matches in database = {}".format(str(self.db.countPlayerMatches(is_eight_ball))))
        

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
    
    def getOpponentTeamName(self, my_team_name, division_link):
        # Go to division link
        # Find and click on your team name
        # Go down their schedule and get the team name for the next match that hasn't been played
        self.createWebDriver()
        self.navigateToTeamPage(division_link, my_team_name)

        header_texts = ['Team Schedule & Results', 'Playoffs']
        for header_text in header_texts:
            header = self.driver.find_element(By.XPATH, "//h2 [contains( text(), '{}')]".format(header_text))
            matches = header.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "a")
            for match in matches:
                if '@' in match.text:
                    'WEEK 5\nFeb\n29\nThursday\nPool Gods(24505)\nSir-Scratch-A Lot(24504)\nCity Pool Hall @ 7:00 pm'
                    text_elements = match.text.split('\n')
                    team1 = text_elements[4].split('(')[0]
                    team2 = text_elements[5].split('(')[0]
                    if team1 == my_team_name:
                        return team2
                    else:
                        return team1
                    