from dataClasses.PlayerMatch import PlayerMatch
from dataClasses.Session import Session
from dataClasses.SessionSeason import SessionSeason
from dataClasses.Division import Division
from dataClasses.Team import Team
from dataClasses.Player import Player
from dataClasses.Score import Score
from dataClasses.PlayerResult import PlayerResult
from dataClasses.Format import Format
from utils.utils import *
from utils.asl import *
from src.srcMain.Typechecked import Typechecked
from src.srcMain.DatabaseTypes import DatabaseTypes


class PlayerMatchWithASLConverter(Typechecked):
    def __init__(self):
        pass
    
    def toPlayerMatchWithSql(self, sqlRow: DatabaseTypes.PlayerMatch) -> PlayerMatch:
        sessionId, sessionSeason, sessionYear = sqlRow[:3]
        divisionId, divisionName, dayOfWeek, format = sqlRow[3:7]
        teamMatchId, datePlayed, playerMatchId, teamId1, teamNum1, teamName1 = sqlRow[7:13]
        memberId1, playerName1, currentSkillLevel1, skillLevel1, adjustedSkillLevel1, teamPtsEarned1, playerPtsEarned1, playerPtsNeeded1 = sqlRow[13:21]
        teamId2, teamNum2, teamName2, memberId2, playerName2, currentSkillLevel2, skillLevel2, adjustedSkillLevel2 = sqlRow[21:29]
        teamPtsEarned2, playerPtsEarned2, playerPtsNeeded2 = sqlRow[29:32]

        adjustedSkillLevel1 = getAdjustedSkillLevel(memberId1, skillLevel1, datePlayed)
        adjustedSkillLevel2 = getAdjustedSkillLevel(memberId2, skillLevel2, datePlayed)
        
        session = Session(sessionId, SessionSeason[sessionSeason], sessionYear)
        division = Division(session, divisionId, divisionName, dayOfWeek, Format(format))
        
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