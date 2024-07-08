class Player:
    def __init__(self, memberId: int, playerName: str, currentSkillLevel: int):
        self.memberId = memberId
        self.playerName = playerName
        self.currentSkillLevel = int(currentSkillLevel)
        self.adjustedSkillLevel = None
    def toJson(self):
        return {
            "memberId": self.memberId,
            "playerName": self.playerName,
            "currentSkillLevel": self.currentSkillLevel,
            "adjustedSkillLevel": self.adjustedSkillLevel
        }
    
    def getMemberId(self):
        return self.memberId
    
    def getPlayerName(self):
        return self.playerName
    
    def getCurrentSkillLevel(self):
        return self.currentSkillLevel
    
    def getAdjustedSkillLevel(self):
        return self.adjustedSkillLevel
    
    def setAdjustedSkillLevel(self, adjustedSkillLevel):
        self.adjustedSkillLevel = adjustedSkillLevel
    
    def __eq__(self, player):
        return self.memberId == player.getMemberId()