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