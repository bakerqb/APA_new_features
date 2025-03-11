from utils.asl import *
from dataClasses.Team import Team
from typing import List, Dict
from dataClasses.PlayerMatch import PlayerMatch
from dataClasses.Player import Player
from src.srcMain.Typechecked import Typechecked

class TeamResults(Typechecked):
    def __init__(self, team: Team, playerMatches: List[PlayerMatch], roster: List[Player]):
        self.team = team
        self.roster = roster
        self.playerMatchesPerPlayer = self.toPlayerMatchesPerPlayer(playerMatches)
        
    
    def toPlayerMatchesPerPlayer(self, playerMatches: List[PlayerMatch]) -> Dict:
        playerMatchesPerPlayer = {}
        for player in self.roster:
            playerName = player.getPlayerName()
            playerMatchesPerPlayer[playerName] = {
                "player": player,
                "ASL": getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None),
                "playerMatches": []
            }

            for playerMatch in playerMatches:
                if playerMatch.isPlayedBy(player):
                    playerMatch = playerMatch.properPlayerResultOrderWithPlayer(player)
                    playerMatchesPerPlayer[playerName]["playerMatches"].append(playerMatch)
        return playerMatchesPerPlayer

    def getTeam(self) -> Team:
        return self.team
    
    def getPlayerMatchesPerPlayer(self) -> Dict:
        return self.playerMatchesPerPlayer
    

    

    

