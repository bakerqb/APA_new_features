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
        todayWeekday = datetime.now().weekday()
        mondayWeekday = 0
        thursdayWeekday = 3
        numDaysInWeek = 7
        return (thursdayWeekday - todayWeekday) % numDaysInWeek < (mondayWeekday - todayWeekday) % numDaysInWeek
    
    

    ############### 9 Ball functions ###############

    def scrapeAllNineBallSessionLinks(self) -> None:
        sessionsWithNoData = [89, 91, 92, 93, 100, 101, 105, 106, 110, 114, 115, 116, 120, 121, 122, 126, 127, 128, 131, 132]
        startingSession = self.config.getConfig().get('apaWebsite').get('startingSession')
        currentSession = self.config.getConfig().get('apaWebsite').get('currentSession')
        if self.db.isNineBallDivisionTableFull(currentSession - startingSession - len(sessionsWithNoData) + 1):
            print("NineBallDivision table up to date. No scraping needed")
            return
        
        for sessionId in range(startingSession, currentSession + 1):
            if sessionId in sessionsWithNoData:
                continue
            
            self.apaWebScraper.scrapeSessionLink(sessionId)

    def scrapeAllNineBallData(self) -> None:
        self.scrapeAllSessionLinks()
        for divisionLink in self.db.getNineBallDivisionLinks():
            self.apaWebScraper.scrapeDivision(divisionLink, False)
    
    def scrapeCurrentNineBallSessionData(self) -> None:
        divisionLink = self.config.getConfig().get('nineBallData').get('divisionLink')
        self.apaWebScraper.scrapeDivision(divisionLink, False)

    def getNineBallMatrix(self) -> None:
        self.db.createNineBallMatrix()

    def getNineBallMatrixMedian(self) -> None:
        self.db.createNineBallMatrixMedian()
