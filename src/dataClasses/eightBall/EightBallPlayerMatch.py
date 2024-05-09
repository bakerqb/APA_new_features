import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.utils import *
from dataClasses.IPlayerMatch import IPlayerMatch

class EightBallPlayerMatch(IPlayerMatch):
    def __init__(self):
        pass
    
    def initWithDiv(self, matchDiv, team_name1: str, team_name2: str, playerMatchId: int, teamMatchId: int, datePlayed):
        text_elements = matchDiv.text.split('\n')
        text_elements = remove_elements(text_elements, 'LAG')
        text_elements = remove_elements(text_elements, 'SL')
        text_elements = remove_elements(text_elements, 'Pts Earned')
        text_elements = remove_elements(text_elements, 'GW/GMW')
        
        player_name1 = text_elements[0]
        skill_level1 = text_elements[1]
        match_pts_earned1 = text_elements[2]

        score = text_elements[4]
        score_elements = score.split(' - ')
        score1 = score_elements[0].split('/')
        if len(score1) == 1:
            score1.insert(0, 0)
        score2 = score_elements[1].split('/')
        if len(score2) == 1:
            score2.insert(0, 0)

        games_won1, games_needed1 = score1
        
        games_won2, games_needed2 = score2
        skill_level2 = text_elements[5]
        player_name2 = text_elements[6]
        match_pts_earned2 = text_elements[7]

        return self.initWithDirectInfo(playerMatchId, teamMatchId, player_name1, team_name1, skill_level1, match_pts_earned1, games_won1, games_needed1,
                   player_name2, team_name2, skill_level2, match_pts_earned2, games_won2, games_needed2, datePlayed, True)
    
    def pretty_print(self, player_in_question):
        self.proper_playerResult_order_with_player(player_in_question)
        p1, p2 = self.playerResults
        
        format1 = "{} [SL {}]".format(p1.get_player_name(), p1.get_skill_level())
        format2 = "Match {} of the night".format(self.playerMatchId)
        line1 = "{}{}{}{}{}".format(
            color_player(p1, format1),
            ' '*(40-len(format1)),
            color_player(p2, "{} [SL {}]".format(p2.get_player_name(), p2.get_skill_level())),
            ' '*(40-len(format2)),
            format2
        )
        print(line1)
        format = p1.get_team_name()
        line2 = "{}{}{}".format(
            color_player(p1, "{}".format(p1.get_team_name())),
            ' '*(40-len(format)),
            color_player(p2, p2.get_team_name())
        )
        print(line2)
        format = "{}/{} Games".format(p1.get_score().get_games_won(), p1.get_score().get_games_needed())
        line3 = "{}{}{}".format(
            color_player(p1, format),
            ' '*(40-len(format)),
            color_player(p2, "{}/{} Games".format(p2.get_score().get_games_won(), p2.get_score().get_games_needed()))
        )
        print(line3)
        format = "{} Match Points".format(p1.get_score().get_match_pts_earned())
        line4 = "{}{}{}".format(
            color_player(p1, format),
            ' '*(40-len(format)),
            color_player(p2, "{} Match Points".format(p2.get_score().get_match_pts_earned()))
        )
        print(line4)