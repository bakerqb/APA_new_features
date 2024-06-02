from dataClasses.eightBall.EightBallPlayerMatch import EightBallPlayerMatch
from dataClasses.nineBall.NineBallPlayerMatch import NineBallPlayerMatch
from dataClasses.Division import Division
from dataClasses.Session import Session
from dataClasses.Team import Team
from dataClasses.Player import Player
from dataClasses.IPlayerMatch import IPlayerMatch
from dataClasses.eightBall.EightBallScore import EightBallScore
from dataClasses.nineBall.NineBallScore import NineBallScore
from dataClasses.PlayerResult import PlayerResult

class Converter:
    def __init__(self):
        pass

    def toPlayerMatchWithDiv(self, matchDiv: object, team1: Team, team2: Team, playerMatchId: int, teamMatchId: int, datePlayed: str, isEightBall: bool) -> IPlayerMatch:
        playerMatch = EightBallPlayerMatch() if isEightBall else NineBallPlayerMatch()
        return playerMatch.initWithDiv(matchDiv, team1, team2, playerMatchId, teamMatchId, datePlayed)

    def toPlayerMatchWithSql(self, sqlRow: list):
        # s.sessionId, s.sessionSeason, s.sessionYear
        # d.divisionId, d.divisionName, d.dayOfWeek, d.game
        # tm.teamMatchId, tm.datePlayed, pm.playerMatchId, pr1.teamId, pr1.teamNum, pr1.teamName
        # pr1.memberId, pr1.playerName, pr1.currentSkillLevel, pm.skillLevel1, pr1.matchPtsEarned, pr1.ballPtsEarned, pr1.ballPtsNeeded
        # pr2.teamId, pr2.teamNum, pr2.teamName, pr2.memberId, pr2.playerName, pr2.currentSkillLevel, pm.skillLevel2, " +
        # pr2.matchPtsEarned, pr2.ballPtsEarned, pr2.ballPtsNeeded """
        
        sessionId, sessionSeason, sessionYear = sqlRow[:3]
        divisionId, divisionName, dayOfWeek, game = sqlRow[3:7]
        teamMatchId, datePlayed, playerMatchId, teamId1, teamNum1, teamName1 = sqlRow[7:13]
        memberId1, playerName1, currentSkillLevel1, skillLevel1, matchPtsEarned1, ballPtsEarned1, ballPtsNeeded1 = sqlRow[13:20]
        teamId2, teamNum2, teamName2, memberId2, playerName2, currentSkillLevel2, skillLevel2 = sqlRow[20:27]
        matchPtsEarned2, ballPtsEarned2, ballPtsNeeded2 = sqlRow[27:30]
        

        playerMatch = EightBallPlayerMatch() if game == "8-ball" else NineBallPlayerMatch()
        session = Session(sessionId, sessionSeason, sessionYear)
        division = Division(session, divisionId, divisionName, dayOfWeek, game)
        
        # TODO: figure out how to get the players here. Do we really wanna do another join on the table where you get all the players in the roster?
        # Alternatively you could do another sql query to get all the roster based on the teamId
        # For now we're just hardcoding in the roster as an empty list cuz I can't see a use case where we'd want that at the PlayerMatch level
        team1 = Team(division, teamId1, teamNum1, teamName1, [])
        team2 = Team(division, teamId2, teamNum2, teamName2, [])
        player1 = Player(memberId1, playerName1, currentSkillLevel1)
        player2 = Player(memberId2, playerName2, currentSkillLevel2)
        score1 = EightBallScore(matchPtsEarned1, ballPtsEarned1, ballPtsNeeded1) if game == "8-ball" else NineBallScore(matchPtsEarned1, ballPtsEarned1, ballPtsNeeded1)
        score2 = EightBallScore(matchPtsEarned2, ballPtsEarned2, ballPtsNeeded2) if game == "8-ball" else NineBallScore(matchPtsEarned2, ballPtsEarned2, ballPtsNeeded2)
        playerResults = [PlayerResult(team1, player1, skillLevel1, score1), PlayerResult(team2, player2, skillLevel2, score2)]
        playerMatch.initNormal(playerResults, playerMatchId, teamMatchId, datePlayed)
        return playerMatch
    
    def toDivisionWithSql(self, sqlRow: list):
        # Returns values in format: sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game
        if not sqlRow:
            return None
        
        sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game = sqlRow[0]

        return self.toDivisionWithDirectValues(sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game)
    
    def toDivisionWithDirectValues(self, sessionId, sessionSeason, sessionYear, divisionId, divisionName, dayOfWeek, game):
        session = Session(sessionId, sessionSeason, sessionYear)
        division = Division(session, divisionId, divisionName, dayOfWeek, game)
        return division
    
    def toSessionWithSql(self, sqlRow):
        # Returns values in format: sessionId, sessionSeason, sessionYear
        if not sqlRow:
            return None

        sessionId, sessionSeason, sessionYear = sqlRow[0]
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
    
    def toPlayerWithSql(self, sqlRow):
        # Data comes in the format of: memberId, playerName, currentSkillLevel
        memberId, playerName, currentSkillLevel = sqlRow
        return Player(memberId, playerName, currentSkillLevel)