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
                    playerMatch.proper_playerResult_order_with_player(player)
                    playerMatchesPerPlayer[playerName]["playerMatches"].append(playerMatch)
        return playerMatchesPerPlayer
    
    def toJson(self):
        return {
            "team" : self.team,
            "playerMatchesPerPlayer": { playerName: { "player": playerMatchesPerPlayerItem.get('player').toJson(), "playerMatches": list(map(lambda playerMatch: playerMatch.toJson(), playerMatchesPerPlayerItem.get('playerMatches'))) } for playerName, playerMatchesPerPlayerItem in self.playerMatchesPerPlayer.items()}
        }
    
    def printPlayerMatchesPerPlayer(self) -> None:
        for player in self.playerMatchesPerPlayer.keys():
            print(color_plain_text("\n-------------------- Results for {} --------------------".format(player)))
            for index, player_match in enumerate(self.playerMatchesPerPlayer[player], 1):
                print(color_plain_text("------ Match {} ------".format(str(index))))
                player_match.pretty_print(player)
