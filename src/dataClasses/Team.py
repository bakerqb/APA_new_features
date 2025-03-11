from dataClasses.Player import Player
from dataClasses.Division import Division
from typing import List
from src.srcMain.Typechecked import Typechecked

class Team(Typechecked):
    def __init__(self, division: Division, teamId: int, teamNum: int, teamName: str, players: List[Player]):
        self.division = division
        self.teamId = teamId
        self.teamNum = teamNum
        self.teamName = teamName
        self.players = players

    def addPlayer(self, player: Player) -> None:
        self.players.append(player)

    def getDivision(self) -> Division:
        return self.division
    
    def getTeamId(self) -> int:
        return self.teamId
    
    def getTeamNum(self) -> int:
        return self.teamNum
    
    def getTeamName(self) -> str:
        return self.teamName
    
    def getPlayers(self) -> List[Player]:
        return self.players
    
    def setPlayers(self, players: List[Player]) -> None:
        self.players = players

    def isPlayerOnTeam(self, playerInQuestion: Player) -> bool:
        for player in self.players:
            if player == playerInQuestion:
                return True
        return False
    
    def getMemberIds(self) -> List[int]:
        return list(map(lambda player: player.getMemberId(), self.players))

    def __eq__(self, team) -> bool:
        return self.teamId == team.getTeamId()