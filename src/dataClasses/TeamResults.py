from utils.asl import *
from dataClasses.Team import Team

class TeamResults:
    def __init__(self, team: Team, playerMatches: list, roster: list, decorateWithASL: bool):
        self.team = team
        self.roster = roster
        self.playerMatchesPerPlayer = self.toPlayerMatchesPerPlayer(playerMatches, decorateWithASL)
        
    
    def toPlayerMatchesPerPlayer(self, playerMatches, decorateWithASL):
        playerMatchesPerPlayer = {}
        for player in self.roster:
            playerName = player.getPlayerName()
            playerMatchesPerPlayer[playerName] = {
                "player": player,
                "ASL": getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None, None),
                "playerMatches": []
            }

            for playerMatch in playerMatches:
                if playerMatch.isPlayedBy(player):
                    playerMatch = playerMatch.properPlayerResultOrderWithPlayer(player)
                    playerMatchesPerPlayer[playerName]["playerMatches"].append(playerMatch)
        return playerMatchesPerPlayer
    
    def toJson(self):
        return {
            "team" : self.team.toJson(),
            "playerMatchesPerPlayer": { playerName: { "player": playerMatchesPerPlayerItem.get('player').toJson(), "ASL": playerMatchesPerPlayerItem.get('ASL'), "playerMatches": list(map(lambda playerMatch: playerMatch.toJson(), playerMatchesPerPlayerItem.get('playerMatches'))) } for playerName, playerMatchesPerPlayerItem in self.playerMatchesPerPlayer.items()}
        }
    
    def getTeam(self):
        return self.team
    
    def getPlayerMatchesPerPlayer(self):
        return self.playerMatchesPerPlayer
    

    

    

