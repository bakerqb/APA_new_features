from src.srcMain.ApaWebScraper import ApaWebScraper
from src.srcMain.Config import Config
from src.srcMain.Database import Database
from converter.Converter import Converter
from converter.PlayerMatchWithASLConverter import PlayerMatchWithASLConverter
from dataClasses.TeamResults import TeamResults
from dataClasses.Format import Format
from dataClasses.Division import Division
from converter.PotentialTeamMatchConverter import PotentialTeamMatchConverter
from utils.utils import *
from utils.asl import *
from utils.aslMatrix import *
from srcMain.Typechecked import Typechecked
from typing import Dict

class UseCase(Typechecked):
    def __init__(self):
        self.apaWebScraper = ApaWebScraper()
        self.config = Config()
        self.db = Database()
        self.converter = Converter()
        self.playerMatchWithASLConverter = PlayerMatchWithASLConverter()
        self.potentialTeamMatchConverter = PotentialTeamMatchConverter()

    # ------------------------- Team Results -------------------------
    def getTeamResults(self, teamId: int) -> TeamResults:
        
        format = Format(self.config.getConfig().get("format"))
        teamResultsDb = self.db.getPlayerMatches(None, None, teamId, None, format, None, None, None, None, None)
        teamResultsPlayerMatches = list(map(lambda playerMatch: self.playerMatchWithASLConverter.toPlayerMatchWithSql(playerMatch), teamResultsDb))
        team = self.converter.toTeamWithSql(self.db.getTeam(None, None, teamId))
        results = TeamResults(team, teamResultsPlayerMatches, list(map(lambda player: self.converter.toPlayerWithSql(player), self.db.getTeamRoster(teamId))))
        return results
    
    def getPlayerMatchesForPlayer(self, memberId: int) -> Dict:
        player = self.converter.toPlayerWithSql(self.db.getPlayer(None, None, memberId))
        format = Format(self.config.getConfig().get("format"))
        player.setAdjustedSkillLevel(getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None))
        return {
            "player": player,
            "playerMatches": list(map(lambda playerMatch: self.playerMatchWithASLConverter.toPlayerMatchWithSql(playerMatch).properPlayerResultOrderWithPlayer(player), self.db.getPlayerMatches(None, None, None, memberId, format, None, None, None, None, None)))
        }

    # ------------------------- Divisions -------------------------
    def getDivisions(self, sessionId: int) -> List[Division]:
        return list(map(lambda division: self.converter.toDivisionWithSql(division), self.db.getDivisions(sessionId)))

    # ------------------------- Sessions -------------------------
    def getSessions(self) -> Dict:
        return { "sessions": list(map(lambda session: self.converter.toSessionWithSql(session), self.db.getSessions())) }
    
    # ------------------------- Teams -------------------------
    def getTeams(self, divisionId: int) -> Dict:
        division = self.converter.toDivisionWithSql(self.db.getDivision(divisionId))
        return {
            "teams": list(map(lambda teamRow: self.converter.toTeamWithoutRosterWithSql(teamRow, division), self.db.getTeamsFromDivision(divisionId))),
            "division": division
        }
    
    # ------------------------- Prediction Accuracy Tester -------------------------
    def getPredictionAccuracy(self) -> str:
        format = Format(self.config.getConfig().get("format"))
        playerMatchesSql = self.db.getPlayerMatches(None, None, None, None, format, None, None, None, None, None)
        teamMatches = self.converter.toTeamMatchesWithPlayerMatchesSql(playerMatchesSql)

        numCorrectlyPredictedMatches = 0
        numTeamMatchesNotResultingInTie = len(teamMatches)
        skillLevelMatrix = createASLMatrix(format, self.config.getConfig().get("predictionAccuracy").get("expectedPtsMethod"))

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
                potentialTeamMatch = self.potentialTeamMatchConverter.toPotentialTeamMatchFromTeamMatch(teamMatch, skillLevelMatrix, format)
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