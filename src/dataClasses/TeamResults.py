from utils.asl import *

class TeamResults:
    def __init__(self, teamId: int, playerMatches: list, roster: list, decorateWithASL: bool):
        for playerResult in playerMatches[0].getPlayerResults():
            if playerResult.getTeam().getTeamId() == teamId:
                self.team = playerResult.getTeam()
        self.roster = roster
        self.playerMatchesPerPlayer = self.toPlayerMatchesPerPlayer(playerMatches, decorateWithASL)
        
    
    def toPlayerMatchesPerPlayer(self, playerMatches, decorateWithASL):
        playerMatchesPerPlayer = {}
        for player in self.roster:
            playerName = player.getPlayerName()
            playerMatchesPerPlayer[playerName] = {
                "player": player,
                "ASL": getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel()),
                "playerMatches": []
            }

            for playerMatch in playerMatches:
                if playerMatch.isPlayedBy(player):
                    playerMatch = playerMatch.properPlayerResultOrderWithPlayer(player)
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
            "team" : self.team.toJson(),
            "playerMatchesPerPlayer": { playerName: { "player": playerMatchesPerPlayerItem.get('player').toJson(), "ASL": playerMatchesPerPlayerItem.get('ASL'), "playerMatches": list(map(lambda playerMatch: playerMatch.toJson(), playerMatchesPerPlayerItem.get('playerMatches'))) } for playerName, playerMatchesPerPlayerItem in self.playerMatchesPerPlayer.items()}
        }
    
    def getTeam(self):
        return self.team
    
    def getPlayerMatchesPerPlayer(self):
        return self.playerMatchesPerPlayer
    

    

    

