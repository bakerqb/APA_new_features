import dataClasses.Player as Player

class PotentialPlayerResult:
    def __init__(self, player: Player, expectedPts: int):      
        self.player = player
        self.expectedPts = expectedPts

    def getPlayer(self):
        return self.player
    
    def getExpectedPts(self):
        return self.expectedPts