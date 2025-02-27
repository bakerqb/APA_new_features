from dataClasses.Player import Player
from dataClasses.Team import Team

class PotentialPlayerResult:
    def __init__(self, player: Player, team: Team, expectedPts: int):      
        self.player = player
        self.team = team
        self.expectedPts = expectedPts

    def getPlayer(self):
        return self.player
    
    def getTeam(self):
        return self.team
    
    def getExpectedPts(self):
        return self.expectedPts