from utils.asl import *

class TeamResults:
    def __init__(self, teamId: int, playerMatches: list, roster: list, decorateWithASL: bool):
        for playerResult in playerMatches[0].toJson().get('playerResults'):
            if playerResult.get('team').get('teamId') == teamId:
                self.team = playerResult.get('team')
        self.roster = roster
        self.playerMatchesPerPlayer = self.toPlayerMatchesPerPlayer(playerMatches, decorateWithASL)
        
    
    def toPlayerMatchesPerPlayer(self, playerMatches, decorateWithASL):
        playerMatchesPerPlayer = {}
        for player in self.roster:
            playerName = player.toJson().get('playerName')
            playerMatchesPerPlayer[player.toJson().get('playerName')] = {
                "player": player,
                "ASL": getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel()),
                "playerMatches": []
            }

            for playerMatch in playerMatches:
                if playerMatch.isPlayedBy(player):
                    playerMatch.properPlayerResultOrderWithPlayer(player)
                    '''
                    if decorateWithASL:
                        for playerResult in playerMatch.getPlayerResults():
                            skillLevel = playerResult.getSkillLevel()
                            memberId = playerResult.getPlayer().getMemberId()
                            playerResult.setAdjustedSkillLevel(getAdjustedSkillLevel(memberId, skillLevel))
                    '''
                    playerMatchesPerPlayer[playerName]["playerMatches"].append(playerMatch)
        return playerMatchesPerPlayer
    
    def toJson(self):
        return {
            "team" : self.team,
            "playerMatchesPerPlayer": { playerName: { "player": playerMatchesPerPlayerItem.get('player').toJson(), "ASL": playerMatchesPerPlayerItem.get('ASL'), "playerMatches": list(map(lambda playerMatch: playerMatch.toJson(), playerMatchesPerPlayerItem.get('playerMatches'))) } for playerName, playerMatchesPerPlayerItem in self.playerMatchesPerPlayer.items()}
        }
