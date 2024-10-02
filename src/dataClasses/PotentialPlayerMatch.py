from dataClasses.Player import Player

class PotentialPlayerMatch:
    def __init__(self, potentialPlayerResults: list):
        self.potentialPlayerResults = potentialPlayerResults
        

    def getPotentialPlayerResults(self):
        return self.potentialPlayerResults
    
    def isPlayedBy(self, player: Player):
        for playerResult in self.potentialPlayerResults:
            if playerResult.getPlayer().getPlayerName() == player.getPlayerName():
                return True
        return False

    def properPlayerResultOrderWithPlayer(self, player: Player):
        if not self.potentialPlayerResults[0].getPlayer() == player:
            self.potentialPlayerResults.reverse()
        return self


    def toJson(self):
        return {
            "potentialPlayerResults": list(map(lambda potentialPlayerResult: potentialPlayerResult.toJson(), self.potentialPlayerResults))
        }
    
    def addPotentialPlayerResult(self, potentialPlayerResult):
        self.potentialPlayerResults.append(potentialPlayerResult)
    
    