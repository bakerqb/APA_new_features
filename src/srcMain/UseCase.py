from src.srcMain.ApaWebScraper import ApaWebScraper
from src.srcMain.Config import Config
from src.srcMain.Database import Database
from converter.Converter import Converter
from dataClasses.TeamResults import TeamResults
from converter.PotentialTeamMatchConverter import PotentialTeamMatchConverter
from utils.utils import *
from utils.asl import *

class UseCase:
    def __init__(self):
        self.apaWebScraper = ApaWebScraper()
        self.config = Config()
        self.db = Database()
        self.converter = Converter()
        self.potentialTeamMatchConverter = PotentialTeamMatchConverter()

    # ------------------------- Team Results -------------------------
    def getTeamResults(self, teamId, decorateWithASL) -> dict:
        teamResultsDb = self.db.getPlayerMatches(None, None, teamId, None, None, None, None, None, None, None)
        teamResultsPlayerMatches = list(map(lambda playerMatch: self.converter.toPlayerMatchWithSql(playerMatch), teamResultsDb))
        team = self.converter.toTeamWithSql(self.db.getTeamWithTeamId(teamId))
        results = TeamResults(team, teamResultsPlayerMatches, list(map(lambda player: self.converter.toPlayerWithSql(player), self.db.getTeamRoster(teamId))), decorateWithASL)
        return results
    
    def getPlayerMatchesForPlayer(self, memberId) -> dict:
        player = self.converter.toPlayerWithSql(self.db.getPlayerBasedOnMemberId(memberId))
        return {
            "player": player,
            "playerMatches": list(map(lambda playerMatch: self.converter.toPlayerMatchWithSql(playerMatch).properPlayerResultOrderWithPlayer(player), self.db.getPlayerMatches(None, None, None, memberId, "8-ball", None, None, None, None, None)))
        }
    
    def getPlayerMatchesForPlayer(self, memberId) -> dict:
        player = self.converter.toPlayerWithSql(self.db.getPlayerBasedOnMemberId(memberId))
        return {
            "player": player,
            "playerMatches": list(map(lambda playerMatch: self.converter.toPlayerMatchWithSql(playerMatch).properPlayerResultOrderWithPlayer(player), self.db.getPlayerMatches(None, None, None, memberId, "8-ball", None, None, None, None, None)))
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
    
    # ------------------------- Prediction Accuracy Tester -------------------------
    def getPredictionAccuracy(self):
        db = Database()
        converter = Converter()
        config = Config().getConfig()
        playerMatchesSql = db.getPlayerMatches(None, None, None, None, "8-ball", None, None, None, None, None)
        teamMatches = converter.toTeamMatchesWithPlayerMatchesSql(playerMatchesSql)

        numCorrectlyPredictedMatches = 0
        numTeamMatchesNotResultingInTie = len(teamMatches)
        skillLevelMatrix = createASLMatrix("8-ball", config.get("predictionAccuracy").get("expectedPtsMethod"))

        # For each of the teamMatches:
        #   Determine who actually won the match
        #   Create PotentialTeamMatch with the actual matchups including the expected points value for each matchup
        #   If the team expected to win actually won, increase the counter by 1
        for teamMatch in teamMatches:
            actualWinningTeams = teamMatch.getWinningTeams()
            if len(actualWinningTeams) == 2:
                numTeamMatchesNotResultingInTie -= 1
                continue
            else:
                actualWinningTeam = actualWinningTeams[0]
                potentialTeamMatch = self.potentialTeamMatchConverter.toPotentialTeamMatchFromTeamMatch(teamMatch, skillLevelMatrix)
                expectedWinningTeams = potentialTeamMatch.getExpectedWinningTeams()
                if len(expectedWinningTeams) == 2:
                    numTeamMatchesNotResultingInTie -= 1
                    continue
                else: 
                    expectedWinningTeam = expectedWinningTeams[0]
                    if actualWinningTeam == expectedWinningTeam:
                        numCorrectlyPredictedMatches += 1
            
        correctlyPredictedPercentage = numCorrectlyPredictedMatches/numTeamMatchesNotResultingInTie
        return str(correctlyPredictedPercentage)