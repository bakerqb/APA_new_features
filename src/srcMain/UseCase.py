from src.srcMain.ApaWebScraper import ApaWebScraper
from src.srcMain.Config import Config
from src.srcMain.Database import Database
from converter.Converter import Converter
from dataClasses.TeamResults import TeamResults
from utils.utils import *

class UseCase:
    def __init__(self):
        self.apaWebScraper = ApaWebScraper()
        self.config = Config()
        self.db = Database()
        self.converter = Converter()

    # ------------------------- Team Results -------------------------
    def getTeamResults(self, teamId, decorateWithASL) -> dict:
        teamResultsDb = self.db.getTeamResults(teamId)
        teamResultsPlayerMatches = list(map(lambda playerMatch: self.converter.toPlayerMatchWithSql(playerMatch), teamResultsDb))
        results = TeamResults(int(teamId), teamResultsPlayerMatches, list(map(lambda player: self.converter.toPlayerWithSql(player), self.db.getTeamRoster(teamId))), decorateWithASL)
        return results
    
    def getUpcomingTeamResultsJson(self) -> dict:
        # TODO: Find a way to know what the sessionId, divisionId, and teamId are just based on the info provided in the config
        
        sessionSeason = self.config.getConfig().get('sessionSeasonInQuestion')
        sessionYear = self.config.getConfig().get('sessionYearInQuestion')
        divisionConfig = self.config.get('myLeagues').get('thursday')
        teamName = self.apaWebScraper.getOpponentTeamName(divisionConfig.get('teamName'), divisionConfig.get('divisionLink'), sessionSeason, sessionYear)
        return self.getTeamResultsJson(sessionSeason, sessionYear, teamName)

    def getTeamResultsJson(self, teamId, decorateWithASL) -> dict:
        return self.getTeamResults(teamId, decorateWithASL).toJson()
    

    # ------------------------- Divisions -------------------------
    def getDivisionsJson(self, sessionId):
        return list(map(lambda division: division.toJson(), self.getDivisions(sessionId)))
    
    def getDivisions(self, sessionId):
        return list(map(lambda division: self.converter.toDivisionWithSql(division), self.db.getDivisions(sessionId)))
    
    def scrapeDivision(self) -> dict:
        # TODO: Find a way to know what the sessionId, divisionId, and teamId are just based on the info provided in the config
        
        self.apaWebScraper.scrapeDivision(self.config.getConfig().get('myLeagues').get('thursday').get('divisionLink'))
        


    # ------------------------- Sessions -------------------------
    def getSessions(self):
        return list(map(lambda session: self.converter.toSessionWithSql(session), self.db.getSessions()))
    
    def getSessionsJson(self):
        return {
            "sessions": list(map(lambda session: session.toJson(), self.getSessions()))
        }

    
    # ------------------------- Teams -------------------------
    def getTeamsJson(self, sessionId, divisionId):
        return {
            "teams": list(map(lambda teamRow: { "teamId": teamRow[2], "teamName": teamRow[4] }, self.db.getTeamsFromDivision(sessionId, divisionId)))
        }
    

    # ------------------------- Skill Level -------------------------
    def getSkillLevelMatrix(self) -> None:
        self.db.createSkillLevelMatrix()