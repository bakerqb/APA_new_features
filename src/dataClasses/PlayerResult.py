import dataClasses.Score as Score
import dataClasses.Team as Team
import dataClasses.Player as Player
from src.srcMain.Typechecked import Typechecked

class PlayerResult(Typechecked):
    def __init__(self, team: Team, player: Player, skillLevel: int, score: Score, adjustedSkillLevel: float | None):      
        self.team = team
        self.player = player
        self.skillLevel = skillLevel
        self.score = score
        self.adjustedSkillLevel = adjustedSkillLevel

    def getTeam(self) -> Team:
        return self.team
    
    def getPlayer(self) -> Player:
        return self.player
    
    def getSkillLevel(self) -> int:
        return self.skillLevel
    
    def getScore(self) -> Score:
        return self.score
    
    def getAdjustedSkillLevel(self) -> float:
        return self.adjustedSkillLevel
    
    def setAdjustedSkillLevel(self, asl: float) -> None:
        self.adjustedSkillLevel = asl