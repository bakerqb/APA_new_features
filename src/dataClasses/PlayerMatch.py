from dataClasses.Player import Player
from utils.utils import *

class PlayerMatch:
    def __init__(self, playerResults: list, playerMatchId: int, teamMatchId: int, datePlayed: str):
        self.playerResults = playerResults
        self.playerMatchId = playerMatchId
        self.teamMatchId = teamMatchId
        self.datePlayed = datePlayed
        self.readableDatePlayed = toReadableDateTimeString(datePlayed)

    def getPlayerResults(self):
        return self.playerResults
    
    def getPlayerMatchId(self):
        return self.playerMatchId
    
    def getTeamMatchId(self):
        return self.teamMatchId
    
    def getDatePlayed(self):
        return self.datePlayed
    
    def getReadableDatePlayed(self):
        return self.readableDatePlayed
    
    def isPlayedBy(self, player: Player):
        for playerResult in self.playerResults:
            if playerResult.getPlayer().getPlayerName() == player.getPlayerName():
                return True
        return False

    def properPlayerResultOrderWithPlayer(self, player: Player):
        if not self.playerResults[0].getPlayer() == player:
            self.playerResults.reverse()
        return self


    def toJson(self):
        return {
            "playerResults": list(map(lambda playerResult: playerResult.toJson(), self.playerResults)),
            "playerMatchId": self.playerMatchId,
            "teamMatchId": self.teamMatchId,
            "datePlayed": self.datePlayed,
            "readableDatePlayed": self.readableDatePlayed
        }
    
    