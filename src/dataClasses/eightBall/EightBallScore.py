import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dataClasses.IScore import IScore


class EightBallScore(IScore):
    def __init__(self, match_pts_earned: int, games_won: int, games_needed: int):
        self.match_pts_earned = int(match_pts_earned)
        self.games_won = int(games_won)
        self.games_needed = int(games_needed)

    def toJson(self):
        return {
            "match_pts_earned": self.match_pts_earned,
            "games_won": self.games_won,
            "games_needed":self.games_needed
        }
    
    def get_match_pts_earned(self):
        return self.match_pts_earned
    
    def get_games_won(self):
        return self.games_won
    
    def get_games_needed(self):
        return self.games_needed
    
    def get_did_win(self):
        return self.match_pts_earned > 1