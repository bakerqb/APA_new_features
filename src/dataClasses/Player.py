from src.srcMain.Typechecked import Typechecked

class Player(Typechecked):
    def __init__(self, memberId: int, playerName: str, currentSkillLevel: int):
        self.memberId = memberId
        self.playerName = playerName
        self.currentSkillLevel = int(currentSkillLevel)
        self.adjustedSkillLevel = None
    
    def getMemberId(self) -> int:
        return self.memberId
    
    def getPlayerName(self) -> str:
        return self.playerName
    
    def getCurrentSkillLevel(self) -> int:
        return self.currentSkillLevel
    
    def getAdjustedSkillLevel(self) -> float:
        return self.adjustedSkillLevel
    
    def setAdjustedSkillLevel(self, adjustedSkillLevel: float) -> None:
        self.adjustedSkillLevel = adjustedSkillLevel
    
    def __eq__(self, player) -> bool:
        return self.memberId == player.getMemberId()
    
    def __lt__(self, player) -> bool:
        return self.currentSkillLevel < player.getCurrentSkillLevel()
    
    def __le__(self, player) -> bool:
        return self.currentSkillLevel <= player.getCurrentSkillLevel()
    
    def __gt__(self, player) -> bool:
        return self.currentSkillLevel > player.getCurrentSkillLevel()
    
    def __ge__(self, player) -> bool:
        return self.currentSkillLevel >= player.getCurrentSkillLevel()
