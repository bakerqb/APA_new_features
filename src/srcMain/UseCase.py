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
        teamResultsDb = self.db.getPlayerMatches(None, teamId, None, None, None, None, None)
        teamResultsPlayerMatches = list(map(lambda playerMatch: self.converter.toPlayerMatchWithSql(playerMatch), teamResultsDb))
        team = self.converter.toTeamWithSql(self.db.getTeamWithTeamId(teamId))
        results = TeamResults(team, teamResultsPlayerMatches, list(map(lambda player: self.converter.toPlayerWithSql(player), self.db.getTeamRoster(teamId))), decorateWithASL)
        return results
    
    def getPlayerMatchesForPlayer(self, memberId) -> dict:
        player = self.converter.toPlayerWithSql(self.db.getPlayerBasedOnMemberId(memberId))
        return {
            "player": player,
            "playerMatches": list(map(lambda playerMatch: self.converter.toPlayerMatchWithSql(playerMatch).properPlayerResultOrderWithPlayer(player), self.db.getPlayerMatches(None, None, memberId, "8-ball", 15, None, None)))
        }

    # ------------------------- Divisions -------------------------
    def getDivisions(self, sessionId):
        return list(map(lambda division: self.converter.toDivisionWithSql(division), self.db.getDivisions(sessionId)))

    # ------------------------- Sessions -------------------------
    def getSessions(self):
        return { "sessions": list(map(lambda session: self.converter.toSessionWithSql(session), self.db.getSessions())) }
    
    # ------------------------- Teams -------------------------
    def getTeams(self, divisionId):
        db = Database()
        converter = Converter()
        division = converter.toDivisionWithSql(db.getDivision(divisionId))
        return {
            "teams": list(map(lambda teamRow: self.converter.toTeamWithoutRosterWithSql(teamRow, division), self.db.getTeamsFromDivision(divisionId))),
            "division": division
        }