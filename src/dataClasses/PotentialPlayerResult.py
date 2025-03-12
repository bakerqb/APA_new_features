from dataClasses.Player import Player
from dataClasses.Team import Team
from src.srcMain.Typechecked import Typechecked

class PotentialPlayerResult:
    def __init__(self, player: Player, team: Team, expectedPts: float):      
        self.player = player
        self.team = team
        self.expectedPts = expectedPts

    def getPlayer(self) -> Player:
        return self.player
    
    def getTeam(self) -> Team:
        return self.team
    
    def getExpectedPts(self) -> float:
        return self.expectedPts