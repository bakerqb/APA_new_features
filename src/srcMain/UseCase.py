from src.srcMain.ApaWebScraper import ApaWebScraper
from src.srcMain.Config import Config
from src.srcMain.Database import Database
from converter.Converter import Converter
from dataClasses.TeamResults import TeamResults
from datetime import datetime
import math
from utils.utils import *

class UseCase:
    def __init__(self):
        self.apaWebScraper = ApaWebScraper()
        self.config = Config()
        self.db = Database()
        self.converter = Converter()


    ############### Game agnostic functions ###############

    # ------------------------- Scraping -------------------------
    def scrapeUpcomingTeamResults(self) -> None:
        # isEightBall = self.isEightBallUpcoming()
        isEightBall = True
        sessionConfig = self.config.getSessionConfig(isEightBall)
        self.apaWebScraper.scrapeDivision(sessionConfig.get('divisionLink'), isEightBall)

    # ------------------------- Getting -------------------------
    def getUpcomingTeamResultsJson(self) -> dict:
        isEightBall = self.isEightBallUpcoming()
        sessionSeason = self.config.getConfig().get('sessionSeasonInQuestion')
        sessionYear = self.config.getConfig().get('sessionYearInQuestion')
        sessionConfig = self.config.getSessionConfig(isEightBall)
        teamName = self.apaWebScraper.getOpponentTeamName(sessionConfig.get('myTeamName'), sessionConfig.get('divisionLink'))
        return self.getTeamResultsJson(sessionSeason, sessionYear, teamName, isEightBall)

    def getTeamResultsJson(self, teamId, decorateWithASL) -> dict:
        return self.getTeamResults(teamId, decorateWithASL).toJson()
    
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
    
    def getTeamResults(self, teamId, decorateWithASL) -> dict:
        #TODO: rewrite sql query that corresponds to this. Join everything in the sql query. Write a converter (most likely rewriting the toPlayerMatchWithSql function)
        
        teamResultsDb = self.db.getTeamResults(teamId)
        teamResultsPlayerMatches = list(map(lambda playerMatch: self.converter.toPlayerMatchWithSql(playerMatch), teamResultsDb))
        return TeamResults(int(teamId), teamResultsPlayerMatches, list(map(lambda player: self.converter.toPlayerWithSql(player), self.db.getTeamRoster(teamId))), decorateWithASL)
    
    





    ############### 9 Ball functions ###############
    def getNineBallMatrix(self) -> None:
        self.db.createNineBallMatrix()

    def getNineBallMatrixMedian(self) -> None:
        self.db.createNineBallMatrixMedian()


    ################ Helper functions ###############
    def isEightBallUpcoming(self) -> bool:
        todayWeekday = datetime.now().weekday()
        mondayWeekday = 0
        thursdayWeekday = 3
        numDaysInWeek = 7
        return (thursdayWeekday - todayWeekday) % numDaysInWeek < (mondayWeekday - todayWeekday) % numDaysInWeek