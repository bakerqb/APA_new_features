from dataClasses.eightBall.EightBallPlayerMatch import EightBallPlayerMatch
from dataClasses.nineBall.NineBallPlayerMatch import NineBallPlayerMatch
from dataClasses.Division import Division
from dataClasses.Session import Session
from dataClasses.Team import Team
from dataClasses.Player import Player
from dataClasses.IPlayerMatch import IPlayerMatch

class Converter:
    def __init__(self):
        pass

    def toPlayerMatchWithDiv(self, matchDiv: object, team1: Team, team2: Team, playerMatchId: int, teamMatchId: int, datePlayed: str, isEightBall: bool) -> IPlayerMatch:
        playerMatch = EightBallPlayerMatch() if isEightBall else NineBallPlayerMatch()
        return playerMatch.initWithDiv(matchDiv, team1, team2, playerMatchId, teamMatchId, datePlayed)

    def toPlayerMatchWithSql(self, sqlRow: list, isEightBall: bool):
        player_match_id = sqlRow[0]
        team_match_id = sqlRow[1]
        player_name1 = sqlRow[2]
        team_name1 = sqlRow[3]
        skill_level1 = sqlRow[4]
        match_pts_earned1 = sqlRow[5]
        games_won1 = sqlRow[6]
        games_needed1 = sqlRow[7]

        player_name2 = sqlRow[8]
        team_name2 = sqlRow[9]
        skill_level2 = sqlRow[10]
        match_pts_earned2 = sqlRow[11]
        games_won2 = sqlRow[12]
        games_needed2 = sqlRow[13]
        date_played = sqlRow[14]

        playerMatch = EightBallPlayerMatch() if isEightBall else NineBallPlayerMatch()
        return playerMatch.initWithDirectInfo(player_match_id, team_match_id, player_name1, team_name1, skill_level1, match_pts_earned1, games_won1, games_needed1,
                   player_name2, team_name2, skill_level2, match_pts_earned2, games_won2, games_needed2, date_played, isEightBall)
    
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
        # Data comes in the format of list(divisionId, teamId, teamNum, teamName, memberId, playerName, currentSkillLevel)
        team = None
        for row in sqlRows:
            divisionId, teamId, teamNum, teamName, memberId, playerName, currentSkillLevel = row
            if team is None:
                team = Team(self.toDivisionWithSql(self.db.getDivision(divisionId)), teamId, teamNum, teamName, [])
            team.addPlayer(Player(memberId, playerName, currentSkillLevel))
        return team
    
    def toPlayerWithSql(self, sqlRow):
        # Data comes in the format of: memberId, playerName, currentSkillLevel
        memberId, playerName, currentSkillLevel = sqlRow
        return Player(memberId, playerName, currentSkillLevel)