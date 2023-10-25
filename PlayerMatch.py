from PlayerResult import PlayerResult
from Score import Score
from utils.utils import *

class PlayerMatch:
    def __init__(self, matchText: str, team_name1: str, team_name2: str):
        mapper = NineBallSkillLevelMapper()
        
        text_elements = matchText.split('\n')
        text_elements = self.remove_elements(text_elements, 'LAG')
        text_elements = self.remove_elements(text_elements, 'SL')
        text_elements = self.remove_elements(text_elements, 'Pts Earned')
        text_elements = self.remove_elements(text_elements, 'PE/PN')
        
        player_name1 = text_elements[0]
        match_pts_earned1 = text_elements[2]

        score = text_elements[4]
        score_elements = score.split(' - ')
        score1 = score_elements[0].split('/')
        if len(score1) == 1:
            score1.insert(0, 0)
        score2 = score_elements[1].split('/')
        if len(score2) == 1:
            score2.insert(0, 0)

        ball_pts_earned1, ball_pts_needed1 = score1
        skill_level1 = mapper.get_map().get(ball_pts_needed1)
        ball_pts_earned2, ball_pts_needed2 = score2

        skill_level2 = mapper.get_map().get(ball_pts_needed2)
        player_name2 = text_elements[6]
        match_pts_earned2 = text_elements[7]

        score1 = Score(match_pts_earned1, ball_pts_earned1, ball_pts_needed1)
        score2 = Score(match_pts_earned2, ball_pts_earned2, ball_pts_needed2)

        self.playerResults = []
        self.playerResults.append(PlayerResult(team_name1, player_name1, skill_level1, score1))
        self.playerResults.append(PlayerResult(team_name2, player_name2, skill_level2, score2))

    def remove_elements(self, test_list, item): 
        res = list(filter((item).__ne__, test_list)) 
        return res

    def getPlayerMatchResult(self):
        return self.playerResults
    
    def isPlayedBy(self, player_name: str):
        for playerResult in self.playerResults:
            if not player_name:
                return True
            if player_name == playerResult.get_player_name():
                return True
        return False
    
    def pretty_print(self, player_in_question):
        
        if (self.playerResults[0].get_player_name() != player_in_question):
            self.playerResults.reverse()
        p1, p2 = self.playerResults
        
        format = "{} [SL {}]".format(p1.get_player_name(), p1.get_skill_level())
        line1 = "{}{}{}".format(
            color_player(p1, format),
            ' '*(40-len(format)),
            color_player(p2, "{} [SL {}]".format(p2.get_player_name(), p2.get_skill_level()))
        )
        print(line1)
        format = p1.get_team_name()
        line2 = "{}{}{}".format(
            color_player(p1, "{}".format(p1.get_team_name())),
            ' '*(40-len(format)),
            color_player(p2, p2.get_team_name())
        )
        print(line2)
        format = "{}/{} Balls".format(p1.get_score().get_ball_pts_earned(), p1.get_score().get_ball_pts_needed())
        line3 = "{}{}{}".format(
            color_player(p1, format),
            ' '*(40-len(format)),
            color_player(p2, "{}/{} Balls".format(p2.get_score().get_ball_pts_earned(), p2.get_score().get_ball_pts_needed()))
        )
        print(line3)
        format = "{} Match Points".format(p1.get_score().get_match_pts_earned())
        line4 = "{}{}{}".format(
            color_player(p1, format),
            ' '*(40-len(format)),
            color_player(p2, "{} Match Points".format(p2.get_score().get_match_pts_earned()))
        )
        print(line4)

        
    
    