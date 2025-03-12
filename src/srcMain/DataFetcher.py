from srcMain.Typechecked import Typechecked
from srcMain.Database import Database
from converter.Converter import Converter
from converter.PlayerMatchWithASLConverter import PlayerMatchWithASLConverter
from dataClasses.Format import Format
from typing import Tuple, List
from dataClasses.PlayerMatch import PlayerMatch
from dataClasses.Team import Team
from dataClasses.Player import Player
from dataClasses.TeamResults import TeamResults
from dataClasses.Division import Division
from dataClasses.Session import Session
from dataClasses.TeamMatch import TeamMatch
from srcMain.Config import Config
from utils.asl import *


class DataFetcher(Typechecked):
    def __init__(self):
        self.db = Database()
        self.converter = Converter()
        self.playerMatchWithASLConverter = PlayerMatchWithASLConverter()
        self.config = Config()
    
    def getPlayerMatches(self, sessionId: int | None, divisionId: int | None, teamId: int | None,
                         memberId: int | None, format: Format, limit: int | None, datePlayed: str | None,
                         playerMatchId: int | None, adjustedSkillLevel1range: Tuple[int] | None,
                         adjustedSkillLevel2range: Tuple[int] | None, player: Player | None) -> List[PlayerMatch]:
        playerMatchesDb = self.db.getPlayerMatches(sessionId, divisionId, teamId, memberId, format, limit, datePlayed, playerMatchId, adjustedSkillLevel1range, adjustedSkillLevel2range)
        playerMatches = list(map(lambda playerMatch: self.playerMatchWithASLConverter.toPlayerMatchWithSql(playerMatch) if player is None else self.playerMatchWithASLConverter.toPlayerMatchWithSql(playerMatch).properPlayerResultOrderWithPlayer(player), playerMatchesDb))
        return playerMatches
    
    def getTeamMatchesWithoutASL(self, sessionId: int | None, divisionId: int | None, teamId: int | None,
                         memberId: int | None, format: Format, limit: int | None, datePlayed: str | None,
                         playerMatchId: int | None, adjustedSkillLevel1range: Tuple[int] | None,
                         adjustedSkillLevel2range: Tuple[int] | None) -> List[TeamMatch]:
        playerMatchesDb = self.db.getPlayerMatches(sessionId, divisionId, teamId, memberId, format, limit, datePlayed, playerMatchId, adjustedSkillLevel1range, adjustedSkillLevel2range)
        teamMatches = self.converter.toTeamMatchesWithPlayerMatchesSql(playerMatchesDb)

        return teamMatches
    
    
    def getTeam(self, teamNum: int | None, divisionId: int | None, teamId: int | None) -> Team:
        teamDb = self.db.getTeam(teamNum, divisionId, teamId)
        team = self.converter.toTeamWithSql(teamDb)
        return team
    
    def getTeamPlayers(self, teamId: int) -> List[Player]:
        playersDb = self.db.getTeamRoster(teamId)
        players = list(map(lambda player: self.converter.toPlayerWithSql(player), playersDb))
        return players
    
    def getTeamResults(self, teamId: int) -> TeamResults:
        format = Format(self.config.getConfig().get("format"))
        playerMatches = self.getPlayerMatches(None, None, teamId, None, format, None, None, None, None, None, None)
        team = self.getTeam(None, None, teamId)
        teamPlayers = self.getTeamPlayers(teamId)
        results = TeamResults(team, playerMatches, teamPlayers)
        return results
    
    def getPlayer(self, teamId: int | None, playerName: str | None, memberId: int | None) -> Player:
        playerDb = self.db.getPlayer(teamId, playerName, memberId)
        player = self.converter.toPlayerWithSql(playerDb)
        player.setAdjustedSkillLevel(getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None))
        return player
    
    def getConfigFormat(self):
        return Format(self.config.getConfig().get("format"))
    
    def getFormatForDivision(self, divisionId):
        return self.db.getFormat(divisionId)
    
    def getDivisions(self, sessionId: int) -> List[Division]:
        divisionsDb = self.db.getDivisions(sessionId)
        divisions = list(map(lambda division: self.converter.toDivisionWithSql(division), divisionsDb))
        return divisions
    
    def getSessions(self) -> List[Session]:
        sessionsDb = self.db.getSessions()
        sessions = list(map(lambda session: self.converter.toSessionWithSql(session), sessionsDb))
        return sessions
    
    def getSession(self, sessionId: int) -> Session:
        sessionDb = self.db.getSession(sessionId)
        session = self.converter.toSessionWithSql(sessionDb)
        return session
    
    def getDivision(self, divisionId: int) -> Division:
        divisionDb = self.db.getDivision(divisionId)
        division = self.converter.toDivisionWithSql(divisionDb)
        return division
    
    def getTeams(self, division: Division) -> List[Team]:
        teamsWithoutRosterDb = self.db.getTeamsFromDivision(division.getDivisionId())
        teams = list(map(lambda teamRow: self.converter.toTeamWithoutRosterWithSql(teamRow, division), teamsWithoutRosterDb))
        return teams
    
    def shouldDisplayTeamMatchupFeature(self, divisionId: int) -> bool:
        format = self.getFormatForDivision(divisionId)
        sessionInQuestion = self.getDivision(divisionId).getSession()
        mostRecentSession = self.converter.toSessionWithSql(db.getSession(db.getMostRecentSessionId(format)))
        previousSession = mostRecentSession.getPreviousSession()
        return sessionInQuestion == mostRecentSession or sessionInQuestion == previousSession
    
    def getExpectedPtsMethod(self):
        return self.config.getConfig().get("predictionAccuracy").get("expectedPtsMethod")