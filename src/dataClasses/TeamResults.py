from utils.utils import color_plain_text

class TeamResults:
    def __init__(self, teamId: int, playerMatches: list, roster: list):
        for playerResult in playerMatches[0].toJson().get('playerResults'):
            if playerResult.get('team').get('teamId') == teamId:
                self.team = playerResult.get('team')
        self.roster = roster
        self.playerMatchesPerPlayer = self.toPlayerMatchesPerPlayer(playerMatches)
        
    
    def toPlayerMatchesPerPlayer(self, playerMatches):
        playerMatchesPerPlayer = {}
        for player in self.roster:
            playerName = player.toJson().get('playerName')
            playerMatchesPerPlayer[player.toJson().get('playerName')] = {
                "player": player,
                "playerMatches": []
            }

            for playerMatch in playerMatches:
                if playerMatch.isPlayedBy(player):
                    playerMatch.properPlayerResultOrderWithPlayer(player)
                    playerMatchesPerPlayer[playerName]["playerMatches"].append(playerMatch)
        return playerMatchesPerPlayer
    
    def toJson(self):
        return {
            "team" : self.team,
            "playerMatchesPerPlayer": { playerName: { "player": playerMatchesPerPlayerItem.get('player').toJson(), "playerMatches": list(map(lambda playerMatch: playerMatch.toJson(), playerMatchesPerPlayerItem.get('playerMatches'))) } for playerName, playerMatchesPerPlayerItem in self.playerMatchesPerPlayer.items()}
        }
