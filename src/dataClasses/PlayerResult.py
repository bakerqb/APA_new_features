import dataClasses.IScore as IScore

class PlayerResult:
    def __init__(self, team_name: str, player_name: str, skill_level: int, score: IScore):
        self.team_name = team_name
        self.player_name = player_name
        self.skill_level = skill_level
        self.score = score

    def toJson(self):
        return {
            "team_name": self.team_name,
            "player_name": self.player_name,
            "skill_level": self.skill_level,
            "score": self.score.toJson()
        }
    
    def get_player_name(self):
        return self.player_name
    
    def get_team_name(self):
        return self.team_name
    
    def get_skill_level(self):
        return self.skill_level
    
    def get_score(self):
        return self.score