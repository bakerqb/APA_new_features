import Score

class PlayerResult:
    def __init__(self, team_name: str, player_name: str, skill_level: int, score: Score):
        self.team_name = team_name
        self.player_name = player_name
        self.skill_level = skill_level
        self.score = score
        self.did_win = score.get_match_pts_earned() > 10

    def get_player_result(self):
        return {
            "team_name": self.team_name,
            "player_name": self.player_name,
            "skill_level": self.skill_level,
            "score": self.score.get_score(),
            "did_win": self.did_win
        }
    
    def get_player_name(self):
        return self.player_name
    
    def get_team_name(self):
        return self.team_name
    
    def get_skill_level(self):
        return self.skill_level
    
    def get_score(self):
        return self.score
    
    def get_did_win(self):
        return self.did_win