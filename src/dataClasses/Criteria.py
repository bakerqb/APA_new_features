class Criteria:
    def __init__(self, memberId: int, playerName: str, minSkillLevel: int, maxSkillLevel: int, dateLastPlayed):
        self.memberId = memberId
        self.playerName = playerName
        self.minSkillLevel = minSkillLevel
        self.maxSkillLevel = maxSkillLevel
        self.dateLastPlayed = dateLastPlayed

    def getMemberId(self):
        return self.memberId
    
    def getPlayerName(self):
        return self.playerName
    
    def getMinSkillLevel(self):
        return self.minSkillLevel
    
    def getMaxSkillLevel(self):
        return self.maxSkillLevel
    
    def getDateLastPlayed(self):
        return self.dateLastPlayed