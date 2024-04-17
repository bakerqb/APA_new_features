from dataClasses.eightBall.EightBallPlayerMatch import EightBallPlayerMatch
from dataClasses.nineBall.NineBallPlayerMatch import NineBallPlayerMatch
from dataClasses.IPlayerMatch import IPlayerMatch

class Converter:
    def __init__(self):
        pass

    def toEightBallPlayerMatch(self, sqlRow):
        
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

        eightBallPlayerMatch = EightBallPlayerMatch()
        eightBallPlayerMatch.initWithDirectInfo(player_match_id, team_match_id, player_name1, team_name1, skill_level1, match_pts_earned1, games_won1, games_needed1,
                   player_name2, team_name2, skill_level2, match_pts_earned2, games_won2, games_needed2)
        return eightBallPlayerMatch

    def toNineBallPlayerMatch(self, sqlRow):
        
        player_match_id = sqlRow[0]
        team_match_id = sqlRow[1]
        player_name1 = sqlRow[2]
        team_name1 = sqlRow[3]
        skill_level1 = sqlRow[4]
        match_pts_earned1 = sqlRow[5]
        ball_pts_earned1 = sqlRow[6]
        ball_pts_needed1 = sqlRow[7]

        player_name2 = sqlRow[8]
        team_name2 = sqlRow[9]
        skill_level2 = sqlRow[10]
        match_pts_earned2 = sqlRow[11]
        ball_pts_earned2 = sqlRow[12]
        ball_pts_needed2 = sqlRow[13]

        nineBallPlayerMatch = NineBallPlayerMatch()
        nineBallPlayerMatch.initWithDirectInfo(player_match_id, team_match_id, player_name1, team_name1, skill_level1, match_pts_earned1, ball_pts_earned1, ball_pts_needed1,
                   player_name2, team_name2, skill_level2, match_pts_earned2, ball_pts_earned2, ball_pts_needed2)
        return nineBallPlayerMatch



