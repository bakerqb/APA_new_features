from ApaWebScraper import ApaWebScraper
from Config import Config
from Database import Database
from converter.Converter import Converter
from utils.utils import color_plain_text
from datetime import datetime

class UseCase:
    def __init__(self):
        self.apaWebScraper = ApaWebScraper()
        self.config = Config().getConfig()
        self.db = Database()
        self.converter = Converter()

    ############### Game agnostic functions ###############
    def printPlayerMatchesForPlayer(self, playerName, playerMatches):
        print(color_plain_text("\n-------------------- Results for {} --------------------".format(playerName)))
        i = 1
        for player_match in playerMatches:
            print(color_plain_text("------ Match {} ------".format(str(i))))
            player_match.pretty_print(playerName)
            i += 1
    
    def getUpcomingTeamResults(self):
        isEightBall = self.isEightBallUpcoming()
        if isEightBall:
            eight_ball_data = self.config.get('eight_ball_data')
            self.apaWebScraper.scrapeDivision(eight_ball_data.get('division_link'), True)
        else:
            nine_ball_data = self.config.get('nine_ball_data')
            self.apaWebScraper.scrapeDivision(nine_ball_data.get('division_link'), False)

    def printUpcomingTeamResults(self):
        isEightBall = self.isEightBallUpcoming()
        if isEightBall:
            eight_ball_data = self.config.get('eight_ball_data')
            sessionSeason = self.config.get('session_season_in_question')
            sessionYear = self.config.get('session_year_in_question')
            teamName = self.apaWebScraper.getOpponentTeamName(eight_ball_data.get('my_team_name'), eight_ball_data.get('division_link'))
            
            self.printEightBallTeamResults(sessionSeason, sessionYear, teamName)
        else:
            nine_ball_data = self.config.get('nine_ball_data')

            sessionSeason = self.config.get('session_season_in_question')
            sessionYear = self.config.get('session_year_in_question')
            teamName = self.apaWebScraper.getOpponentTeamName(nine_ball_data.get('my_team_name'), nine_ball_data.get('division_link'))
            self.printNineBallTeamResults(sessionSeason, sessionYear, teamName)
    
    def isEightBallUpcoming(self):
        today_weekday = datetime.now().weekday()
        monday_weekday = 0
        thursday_weekday = 3
        num_days_in_week = 7
        return (thursday_weekday - today_weekday) % num_days_in_week < (monday_weekday - today_weekday) % num_days_in_week
    

    ############### 9 Ball functions ###############

    def scrapeAllNineBallSessionLinks(self):
        sessions_with_no_data = [89, 91, 92, 93, 100, 101, 105, 106, 110, 114, 115, 116, 120, 121, 122, 126, 127, 128, 131, 132]
        starting_session = self.config.get('apa_website').get('starting_session')
        current_session = self.config.get('apa_website').get('current_session')
        if self.db.isNineBallDivisionTableFull(current_session - starting_session - len(sessions_with_no_data) + 1):
            print("NineBallDivision table up to date. No scraping needed")
            return
        
        for sessionId in range(starting_session, current_session + 1):
            if sessionId in sessions_with_no_data:
                continue
            
            self.apaWebScraper.scrapeSessionLink(sessionId)

    def scrapeAllNineBallData(self):
        self.scrapeAllSessionLinks()
        for divisionLink in self.db.getNineBallDivisionLinks():
            self.apaWebScraper.scrapeDivision(divisionLink, False)
    
    def scrapeCurrentNineBallSessionData(self):
        division_link = self.config.get('nine_ball_data').get('division_link')
        self.apaWebScraper.scrapeDivision(division_link, False)

    def getNineBallMatrix(self):
        self.db.createNineBallMatrix()

    def getNineBallMatrixMedian(self):
        self.db.createNineBallMatrixMedian()

    def printNineBallTeamResults(self, sessionSeason, sessionYear, teamName):
        playerMatches = self.db.getNineBallTeamResults(sessionSeason, sessionYear, teamName)
        playerMatchObjList = []
        for playerMatch in playerMatches:
            playerMatchObjList.append(self.converter.toNineBallPlayerMatch(playerMatch))
        roster = self.db.getNineBallRoster(sessionSeason, sessionYear, teamName)
        
        playerMatchMap = {}
        for player in roster:
            playerMatchMap[player[0]] = []

        for playerMatchObj in playerMatchObjList:
            for player in roster:
                if playerMatchObj.isPlayedBy(player[0]):
                    playerMatchMap[player[0]].append(playerMatchObj)

        for playerName in playerMatchMap.keys():
            self.printPlayerMatchesForPlayer(playerName, playerMatchMap[playerName])

    
    ############### 8 Ball functions ###############
    
    def scrapeCurrentEightBallSessionData(self):
        division_link = self.config.get('eight_ball_data').get('division_link')
        self.apaWebScraper.scrapeDivision(division_link, True)

    def scrapeAllEightBallData(self):
        self.scrapeAllSessionLinks()
        for divisionLink in self.db.getEightBallDivisionLinks():
            self.apaWebScraper.scrapeDivision(divisionLink, True)
    

    def printEightBallTeamResults(self, sessionSeason, sessionYear, teamName):
        playerMatches = self.db.getEightBallTeamResults(sessionSeason, sessionYear, teamName)
        playerMatchObjList = []
        for playerMatch in playerMatches:
            playerMatchObjList.append(self.converter.toEightBallPlayerMatch(playerMatch))
        roster = self.db.getEightBallRoster(sessionSeason, sessionYear, teamName)
        
        playerMatchMap = {}
        for player in roster:
            playerMatchMap[player[0]] = []

        for playerMatchObj in playerMatchObjList:
            for player in roster:
                if playerMatchObj.isPlayedBy(player[0]):
                    playerMatchMap[player[0]].append(playerMatchObj)

        for playerName in playerMatchMap.keys():
            self.printPlayerMatchesForPlayer(playerName, playerMatchMap[playerName])      
