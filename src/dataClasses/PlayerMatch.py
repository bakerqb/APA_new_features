from dataClasses.Player import Player
from utils.utils import *
from typing import List
from dataClasses.PlayerResult import PlayerResult
from src.srcMain.Typechecked import Typechecked

class PlayerMatch(Typechecked):
    def __init__(self, playerResults: List[PlayerResult], playerMatchId: int, teamMatchId: int, datePlayed: str):
        self.playerResults = playerResults
        self.playerMatchId = playerMatchId
        self.teamMatchId = teamMatchId
        self.datePlayed = datePlayed
        self.readableDatePlayed = toReadableDateTimeString(datePlayed)

    def getPlayerResults(self) -> List[PlayerResult]:
        return self.playerResults
    
    def getPlayerMatchId(self) -> int:
        return self.playerMatchId
    
    def getTeamMatchId(self) -> int:
        return self.teamMatchId
    
    def getDatePlayed(self) -> str:
        return self.datePlayed
    
    def getReadableDatePlayed(self) -> str:
        return self.readableDatePlayed
    
    def isPlayedBy(self, player: Player) -> bool:
        for playerResult in self.playerResults:
            if playerResult.getPlayer().getPlayerName() == player.getPlayerName():
                return True
        return False

    def properPlayerResultOrderWithPlayer(self, player: Player):
        if not self.playerResults[0].getPlayer() == player:
            self.playerResults.reverse()
        return self