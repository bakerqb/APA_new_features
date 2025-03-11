from src.srcMain.Typechecked import Typechecked

class SearchCriteria(Typechecked):
    def __init__(self, memberId: int | None, playerName: str | None, minSkillLevel: int | None, maxSkillLevel: int | None, dateLastPlayed: str | None):
        self.memberId = memberId
        self.playerName = playerName
        self.minSkillLevel = minSkillLevel
        self.maxSkillLevel = maxSkillLevel
        self.dateLastPlayed = dateLastPlayed

    def getMemberId(self) -> int | None:
        return self.memberId
    
    def getPlayerName(self) -> str | None:
        return self.playerName
    
    def getMinSkillLevel(self) -> int | None:
        return self.minSkillLevel
    
    def getMaxSkillLevel(self) -> int | None:
        return self.maxSkillLevel
    
    def getDateLastPlayed(self) -> str | None:
        return self.dateLastPlayed