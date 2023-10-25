class Score:
    def __init__(self, match_pts_earned: int, ball_pts_earned: int, ball_pts_needed: int):
        self.match_pts_earned = int(match_pts_earned)
        self.ball_pts_earned = int(ball_pts_earned)
        self.ball_pts_needed = int(ball_pts_needed)

    def get_score(self):
        return {
            "match_pts_earned": self.match_pts_earned,
            "ball_pts_earned": self.ball_pts_earned,
            "ball_pts_needed":self.ball_pts_needed
        }
    
    def get_match_pts_earned(self):
        return self.match_pts_earned
    
    def get_ball_pts_earned(self):
        return self.ball_pts_earned
    
    def get_ball_pts_needed(self):
        return self.ball_pts_needed