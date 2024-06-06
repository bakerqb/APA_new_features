from src.srcMain.ApaWebScraper import ApaWebScraper
from src.srcMain.Config import Config
from src.srcMain.Database import Database
from converter.Converter import Converter
from dataClasses.TeamResults import TeamResults
from datetime import datetime
import json

class UseCase:
    def __init__(self):
        self.apaWebScraper = ApaWebScraper()
        self.config = Config()
        self.db = Database()
        self.converter = Converter()


    ############### Game agnostic functions ###############
    
    # ------------------------- Printing -------------------------
    def printTeamResults(self, sessionSeason, sessionYear, teamName, isEightBall) -> None:
        self.getTeamResults(sessionSeason, sessionYear, teamName, isEightBall).printPlayerMatchesPerPlayer()

    '''
    def printUpcomingTeamResults(self, sessionId, divisionId, ownTeamId) -> None:
        
        isEightBall = self.isEightBallUpcoming()
        sessionConfig = self.config.getSessionConfig(isEightBall)
        teamName = self.apaWebScraper.getOpponentTeamName(sessionConfig.get('my_team_name'), sessionConfig.get('division_link'))
        self.printTeamResults(sessionSeason, sessionYear, teamName, isEightBall)
    '''
    

    def printUpcomingTeamResultsJson(self) -> None:
        self.printTeamResultsJson(self.getUpcomingTeamResultsJson())

    def printTeamResultsJson(self, sessionSeason, sessionYear, teamName, isEightBall) -> None:
        teamResults = self.getTeamResults(sessionSeason, sessionYear, teamName, isEightBall).toJson()
        file = open('src/resources/teamResults.json', 'w')
        file.write(json.dumps(teamResults, indent=2))

    # ------------------------- Scraping -------------------------
    def scrapeUpcomingTeamResults(self) -> None:
        # isEightBall = self.isEightBallUpcoming()
        isEightBall = True
        sessionConfig = self.config.getSessionConfig(isEightBall)
        self.apaWebScraper.scrapeDivision(sessionConfig.get('division_link'), isEightBall)

    # ------------------------- Getting -------------------------
    def getUpcomingTeamResultsJson(self) -> dict:
        isEightBall = self.isEightBallUpcoming()
        sessionSeason = self.config.getConfig().get('session_season_in_question')
        sessionYear = self.config.getConfig().get('session_year_in_question')
        sessionConfig = self.config.getSessionConfig(isEightBall)
        teamName = self.apaWebScraper.getOpponentTeamName(sessionConfig.get('my_team_name'), sessionConfig.get('division_link'))
        return self.getTeamResultsJson(sessionSeason, sessionYear, teamName, isEightBall)

    def getTeamResultsJson(self, teamId) -> dict:
        return self.getTeamResults(teamId).toJson()
    
    def getDivisionsJson(self, sessionId):
        return list(map(lambda division: division.toJson(), self.getDivisions(sessionId)))
    
    def getDivisions(self, sessionId):
        return list(map(lambda division: self.converter.toDivisionWithSql(division), self.db.getDivisions(sessionId)))

    def getSessionsJson(self):
        return {
            "sessions": list(map(lambda session: session.toJson(), self.getSessions()))
        }

    def getTeamsJson(self, sessionId, divisionId):
        return {
            "teams": list(map(lambda teamRow: { "teamId": teamRow[2], "teamName": teamRow[4] }, self.db.getTeamsFromDivision(sessionId, divisionId)))
        }
    
    def getSessions(self):
        return list(map(lambda session: self.converter.toSessionWithSql(session), self.db.getSessions()))
    
    def getTeamResults(self, teamId) -> dict:
        #TODO: rewrite sql query that corresponds to this. Join everything in the sql query. Write a converter (most likely rewriting the toPlayerMatchWithSql function)
        
        teamResultsDb = self.db.getTeamResults(teamId)
        teamResultsPlayerMatches = list(map(lambda playerMatch: self.converter.toPlayerMatchWithSql(playerMatch), teamResultsDb))
        return TeamResults(int(teamId), teamResultsPlayerMatches, list(map(lambda player: self.converter.toPlayerWithSql(player), self.db.getTeamRoster(teamId))))

    # ------------------------- Helper functions -------------------------
    def isEightBallUpcoming(self) -> bool:
        today_weekday = datetime.now().weekday()
        monday_weekday = 0
        thursday_weekday = 3
        num_days_in_week = 7
        return (thursday_weekday - today_weekday) % num_days_in_week < (monday_weekday - today_weekday) % num_days_in_week
    
    

    ############### 9 Ball functions ###############

    def scrapeAllNineBallSessionLinks(self) -> None:
        sessions_with_no_data = [89, 91, 92, 93, 100, 101, 105, 106, 110, 114, 115, 116, 120, 121, 122, 126, 127, 128, 131, 132]
        starting_session = self.config.getConfig().get('apa_website').get('starting_session')
        current_session = self.config.getConfig().get('apa_website').get('current_session')
        if self.db.isNineBallDivisionTableFull(current_session - starting_session - len(sessions_with_no_data) + 1):
            print("NineBallDivision table up to date. No scraping needed")
            return
        
        for sessionId in range(starting_session, current_session + 1):
            if sessionId in sessions_with_no_data:
                continue
            
            self.apaWebScraper.scrapeSessionLink(sessionId)

    def scrapeAllNineBallData(self) -> None:
        self.scrapeAllSessionLinks()
        for divisionLink in self.db.getNineBallDivisionLinks():
            self.apaWebScraper.scrapeDivision(divisionLink, False)
    
    def scrapeCurrentNineBallSessionData(self) -> None:
        division_link = self.config.getConfig().get('nine_ball_data').get('division_link')
        self.apaWebScraper.scrapeDivision(division_link, False)

    def getNineBallMatrix(self) -> None:
        self.db.createNineBallMatrix()

    def getNineBallMatrixMedian(self) -> None:
        self.db.createNineBallMatrixMedian()
