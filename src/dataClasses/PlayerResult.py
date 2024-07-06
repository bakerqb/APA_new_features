import dataClasses.Score as Score
import dataClasses.Team as Team
import dataClasses.Player as Player

class PlayerResult:
    def __init__(self, team: Team, player: Player, skillLevel: int, score: Score, adjustedSkillLevel: int):      
        self.team = team
        self.player = player
        self.skillLevel = skillLevel
        self.score = score
        self.adjustedSkillLevel = adjustedSkillLevel

    def toJson(self):
        return {
            "team": self.team.toJson(),
            "player": self.player.toJson(),
            "skillLevel": self.skillLevel,
            "score": self.score.toJson(),
            "adjustedSkillLevel": self.adjustedSkillLevel
        }
    
    def getTeam(self):
        return self.team
    
    def getPlayer(self):
        return self.player
    
    def getSkillLevel(self):
        return self.skillLevel
    
    def getScore(self):
        return self.score
    
    def getAdjustedSkillLevel(self):
        return self.adjustedSkillLevel
    
    def setAdjustedSkillLevel(self, asl):
        self.adjustedSkillLevel = asl