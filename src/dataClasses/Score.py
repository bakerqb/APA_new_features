from src.srcMain.Typechecked import Typechecked

class Score(Typechecked):
    def __init__(self, teamPtsEarned: int, playerPtsEarned: int, playerPtsNeeded: int):
        self.teamPtsEarned = teamPtsEarned
        self.playerPtsEarned = playerPtsEarned
        self.playerPtsNeeded = playerPtsNeeded

    def getTeamPtsEarned(self) -> int:
        return self.teamPtsEarned
    
    def getPlayerPtsEarned(self) -> int:
        return self.playerPtsEarned
    
    def getPlayerPtsNeeded(self) -> int:
        return self.playerPtsNeeded