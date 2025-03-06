from dataClasses.Division import Division
from dataClasses.Session import Session
from dataClasses.Team import Team
from dataClasses.Player import Player
from dataClasses.TeamMatch import TeamMatch
from utils.asl import *
from utils.utils import *
from typing import List
from dataClasses.Format import Format

class Converter:
    def __init__(self):
        pass
    
    def toDivisionWithSql(self, sqlRow: list):
        # Returns values in format: sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, format
        if not sqlRow:
            return None
        
        sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, format = sqlRow

        return self.toDivisionWithDirectValues(sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, Format(format))
    
    def toDivisionWithDirectValues(self, sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, format: Format):
        session = Session(sessionId, sessionSeason, sessionYear)
        division = Division(session, divisionId, divisionName, dayOfWeek, format)
        return division
    
    def toSessionWithSql(self, sqlRow):
        # Returns values in format: sessionId, sessionSeason, sessionYear
        if not sqlRow:
            return None

        sessionId, sessionSeason, sessionYear = sqlRow
        return Session(sessionId, sessionSeason, sessionYear)
    
    def toTeamWithSql(self, sqlRows):
        # Data comes in the format of list(sessionId, sessionSeason, sessionYear, 
        # divisionId, divisionName, dayOfWeek, format, teamId, teamNum, 
        # teamName, memberId, playerName, currentSkillLevel)
        team = None
        for row in sqlRows:
            sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, format, teamId, teamNum, teamName, memberId, playerName, currentSkillLevel = row
            if team is None:
                team = Team(
                    self.toDivisionWithDirectValues(
                        sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, Format(format)
                    ),
                    teamId,
                    teamNum,
                    teamName,
                    []
                )
            team.addPlayer(Player(memberId, playerName, currentSkillLevel))
        return team
    
    def toTeamWithoutRosterWithSql(self, sqlRow, division):
        divisionId, teamId, teamNum, teamName = sqlRow
        return Team(division, teamId, teamNum, teamName, [])
    
    def toPlayerWithSql(self, sqlRow):
        # Data comes in the format of: memberId, playerName, currentSkillLevel
        memberId, playerName, currentSkillLevel = sqlRow
        return Player(memberId, playerName, currentSkillLevel)
    
    