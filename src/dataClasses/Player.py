class Player:
    def __init__(self, player_name: str, team_name: str, player_id: str, skill_level: str):
        self.player_name = player_name
        self.team_name = team_name
        self.player_id = player_id
        self.skill_level = int(skill_level)

    def get_player_name(self):
        return self.player_name
    
    def get_team_name(self):
        return self.team_name
    
    def get_player_id(self):
        return self.player_id
    
    def get_skill_level(self):
        return self.skill_level