from dataClasses.Player import Player
from dataClasses.Division import Division

class Team:
    def __init__(self, division: Division, teamId: str, teamNum: int, teamName: str, players: list):
        self.division = division
        self.teamId = teamId
        self.teamNum = teamNum
        self.teamName = teamName
        self.players = players

    def toJson(self):
        return {
            "division": self.division.toJson(),
            "teamId": self.teamId,
            "teamNum": self.teamNum,
            "teamName": self.teamName,
            "players": list(map(lambda player: player.toJson(), self.players))
        }
    
    def addPlayer(self, player: Player):
        self.players.append(player)

    def getDivision(self):
        return self.division
    
    def getTeamId(self):
        return self.teamId
    
    def getTeamNum(self):
        return self.teamNum
    
    def getTeamName(self):
        return self.teamName
    
    def getPlayers(self):
        return self.players
    
    def setPlayers(self, players):
        self.players = players

    def isPlayerOnTeam(self, playerInQuestion: Player):
        for player in self.players:
            if player == playerInQuestion:
                return True
        return False
