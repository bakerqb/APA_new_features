from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import sys
import os
from Config import Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataClasses.nineBall.NineBallPlayerMatch import NineBallPlayerMatch
from dataClasses.eightBall.EightBallPlayerMatch import EightBallPlayerMatch
from Database import Database
import calendar


class ApaWebScraper:
    #### Startup ####
    def __init__(self):
        self.config = Config().getConfig()
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
        username_element = self.driver.find_element(By.ID, 'email')
        username_element.send_keys(self.config.get('apa_credentials').get('email'))
        password_element = self.driver.find_element(By.ID, 'password')
        password_element.send_keys(self.config.get('apa_credentials').get('password'))
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
        table = self.driver.find_element(By.TAG_NAME, "tbody")
        session = self.driver.find_element(By.CLASS_NAME, "m-b-10").text
        sessionSeason, sessionYear = session.split(" ")
        team_links = []
        for row in table.find_elements(By.TAG_NAME, "tr"):
            team_links.append(self.config.get('apa_website').get('base_link') + row.get_attribute("to"))
        for team in team_links:
            self.driver.get(team)
            
            match_links = self.scrapeTeamMatchesForTeam('Team Schedule & Results', sessionSeason, sessionYear, is_eight_ball)
            match_links = match_links + self.scrapeTeamMatchesForTeam('Playoffs', sessionSeason, sessionYear, is_eight_ball)
            print("Total team matches in database = {}".format(self.db.countTeamMatches(is_eight_ball)))
            self.getTeamMatchResults(match_links, is_eight_ball)
        
        

    def scrapeTeamMatchesForTeam(self, headerTitle, sessionSeason, sessionYear, isEightBall):
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
                    self.db.addTeamMatchValue(teamMatchId, apa_datetime, sessionSeason, sessionYear, isEightBall)
                
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
    def getPlayerMatchesFromTeamMatch(self, link, is_eight_ball):
        self.createWebDriver()
        self.driver.get(link)
        if is_eight_ball:
            time.sleep(10)
        teams_header = self.driver.find_element(By.XPATH, "//h3 [contains( text(), 'FINAL SCORE')]")
        teams_text = teams_header.find_element(By.XPATH, "..").text
        team_name1 = teams_text.split('\n')[1]
        team_name2 = teams_text.split('\n')[4]

        matches_header = self.driver.find_element(By.XPATH, "//h3 [contains( text(), 'MATCH BREAKOUT')]")
        matches_div = matches_header.find_element(By.XPATH, "..")
        individual_matches = matches_div.find_elements(By.XPATH, "./*")
        
        player_matches = []
        player_match_id = 0
        team_match_id = link.split('/')[-1]
        for individual_match in individual_matches:
            if 'LAG' not in individual_match.text:
                continue
            player_match_id += 1
            player_match = None
            if not is_eight_ball:
                player_match = NineBallPlayerMatch()
                player_match.initWithDiv(individual_match, team_name1, team_name2, player_match_id, team_match_id)
            else:
                player_match = EightBallPlayerMatch()
                player_match = player_match.initWithDiv(individual_match, team_name1, team_name2, player_match_id, team_match_id)
            if player_match.getPlayerMatchResult()[0].get_skill_level() is not None and player_match.getPlayerMatchResult()[1].get_skill_level() is not None:
                player_matches.append(player_match)
            
        
        return player_matches

    # Loops through all TeamMatches from team
    # Gets all PlayerMatches for entire session
    # Adds PlayerMatches to database
    def getTeamMatchResults(self, match_links, is_eight_ball):
        matches = []
        for match_link in match_links:
            matches = matches + self.getPlayerMatchesFromTeamMatch(match_link, is_eight_ball)
        for match in matches:
            if is_eight_ball:
                self.db.addEightBallPlayerMatchValue(match)
            else:
                self.db.addNineBallPlayerMatchValue(match)
        
        print("Total player matches in database = {}".format(str(self.db.countPlayerMatches(is_eight_ball))))
        

    def getRoster(self):
        self.createWebDriver()
        roster_header = self.driver.find_element(By.XPATH, "//h2 [contains( text(), 'Team Roster')]")
        roster_div = roster_header.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "a")
        roster = []
        for row in roster_div:
            roster.append(row.text)
        return roster
    
    def getOpponentTeamName(self, my_team_name, division_link):
        # Go to division link
        # Find and click on your team name
        # Go down their schedule and get the team name for the next match that hasn't been played
        self.createWebDriver()
        self.navigateToTeamPage(division_link, my_team_name)

        matches_header = self.driver.find_element(By.XPATH, "//h2 [contains( text(), '{}')]".format('Team Schedule & Results'))
        matches = matches_header.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "a")
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
            
        #TODO: Do for playoffs as well


