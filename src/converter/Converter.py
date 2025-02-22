from dataClasses.PlayerMatch import PlayerMatch
from dataClasses.Division import Division
from dataClasses.Session import Session
from dataClasses.Team import Team
from dataClasses.Player import Player
from src.dataClasses.PlayerMatch import PlayerMatch
from dataClasses.TeamMatch import TeamMatch
from dataClasses.Score import Score
from dataClasses.PlayerResult import PlayerResult
from typing import List

class Converter:
    def __init__(self):
        pass

    def toPlayerMatchWithSql(self, sqlRow: list):
        sessionId, sessionSeason, sessionYear = sqlRow[:3]
        divisionId, divisionName, dayOfWeek, game = sqlRow[3:7]
        teamMatchId, datePlayed, playerMatchId, teamId1, teamNum1, teamName1 = sqlRow[7:13]
        memberId1, playerName1, currentSkillLevel1, skillLevel1, adjustedSkillLevel1, teamPtsEarned1, playerPtsEarned1, playerPtsNeeded1 = sqlRow[13:21]
        teamId2, teamNum2, teamName2, memberId2, playerName2, currentSkillLevel2, skillLevel2, adjustedSkillLevel2 = sqlRow[21:29]
        teamPtsEarned2, playerPtsEarned2, playerPtsNeeded2 = sqlRow[29:32]
        
        session = Session(sessionId, sessionSeason, sessionYear)
        division = Division(session, divisionId, divisionName, dayOfWeek, game)
        
        # TODO: figure out how to get the players here. Do we really wanna do another join on the table where you get all the players in the roster?
        # Alternatively you could do another sql query to get all the roster based on the teamId
        # For now we're just hardcoding in the roster as an empty list cuz I can't see a use case where we'd want that at the PlayerMatch level
        team1 = Team(division, teamId1, teamNum1, teamName1, [])
        team2 = Team(division, teamId2, teamNum2, teamName2, [])
        player1 = Player(memberId1, playerName1, currentSkillLevel1)
        player2 = Player(memberId2, playerName2, currentSkillLevel2)
        score1 = Score(teamPtsEarned1, playerPtsEarned1, playerPtsNeeded1)
        score2 = Score(teamPtsEarned2, playerPtsEarned2, playerPtsNeeded2)
        playerResult1 = PlayerResult(team1, player1, skillLevel1, score1, adjustedSkillLevel1)
        playerResult2 = PlayerResult(team2, player2, skillLevel2, score2, adjustedSkillLevel2)
        playerResults = [playerResult1, playerResult2]
        return PlayerMatch(playerResults, playerMatchId, teamMatchId, datePlayed)
        
    
    def toDivisionWithSql(self, sqlRow: list):
        # Returns values in format: sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game
        if not sqlRow:
            return None
        
        sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game = sqlRow

        return self.toDivisionWithDirectValues(sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game)
    
    def toDivisionWithDirectValues(self, sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game):
        session = Session(sessionId, sessionSeason, sessionYear)
        division = Division(session, divisionId, divisionName, dayOfWeek, game)
        return division
    
    def toSessionWithSql(self, sqlRow):
        # Returns values in format: sessionId, sessionSeason, sessionYear
        if not sqlRow:
            return None

        sessionId, sessionSeason, sessionYear = sqlRow
        return Session(sessionId, sessionSeason, sessionYear)
    
    def toTeamWithSql(self, sqlRows):
        # Data comes in the format of list(sessionId, sessionSeason, sessionYear, 
        # divisionId, divisionName, dayOfWeek, game, teamId, teamNum, 
        # teamName, memberId, playerName, currentSkillLevel)
        team = None
        for row in sqlRows:
            sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game, teamId, teamNum, teamName, memberId, playerName, currentSkillLevel = row
            if team is None:
                team = Team(
                    self.toDivisionWithDirectValues(
                        sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game
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
    
    def toTeamMatchesWithPlayerMatchesSql(self, sqlRows) -> List[TeamMatch]:
        teamMatchesMap = {}
        for sqlRow in sqlRows:
            playerMatch = self.toPlayerMatchWithSql(sqlRow)
            teamMatchId = playerMatch.getTeamMatchId()
            if teamMatchId in teamMatches.keys():
                teamMatches[teamMatchId].add(playerMatch)
            else:
                teamMatches[teamMatchId] = [playerMatch]

        teamMatches = []
        for teamMatchId, playerMatches in teamMatchesMap.items():
            datePlayed = playerMatches[0].getDatePlayed()
            teamMatch = TeamMatch(playerMatches, teamMatchId, datePlayed)
            teamMatches.append(teamMatch)

        return teamMatches