class Score():
    def __init__(self, teamPtsEarned: int, playerPtsEarned: int, playerPtsNeeded: int):
        self.teamPtsEarned = int(teamPtsEarned)
        self.playerPtsEarned = int(playerPtsEarned)
        self.playerPtsNeeded = int(playerPtsNeeded)

    def getTeamPtsEarned(self):
        return self.teamPtsEarned
    
    def getPlayerPtsEarned(self):
        return self.playerPtsEarned
    
    def getPlayerPtsNeeded(self):
        return self.playerPtsNeeded