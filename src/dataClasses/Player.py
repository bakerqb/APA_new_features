class Player:
    def __init__(self, memberId: int, playerName: str, currentSkillLevel: int):
        self.memberId = memberId
        self.playerName = playerName
        self.currentSkillLevel = int(currentSkillLevel)

    def toJson(self):
        return {
            "memberId": self.memberId,
            "playerName": self.playerName,
            "currentSkillLevel": self.currentSkillLevel
        }