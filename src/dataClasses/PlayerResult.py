import dataClasses.Score as Score
import dataClasses.Team as Team
import dataClasses.Player as Player

class PlayerResult:
    def __init__(self, team: Team, player: Player, skillLevel: int, score: Score):      
        self.team = team
        self.player = player
        self.skillLevel = skillLevel
        self.score = score
        self.adjustedSkillLevel = None

    def toJson(self):
        return {
            "team": self.team.toJson(),
            "player": self.player.toJson(),
            "skillLevel": self.skillLevel,
            "score": self.score.toJson()
        }
    
    def getTeam(self):
        return self.team
    
    def getPlayer(self):
        return self.player
    
    def getSkillLevel(self):
        return self.skillLevel
    
    def getScore(self):
        return self.score
    
    def setAdjustedSkillLevel(self, skillLevel):
        self.skillLevel = skillLevel