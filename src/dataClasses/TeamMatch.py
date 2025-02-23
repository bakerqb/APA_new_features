from dataClasses.Player import Player
from dataClasses.PlayerMatch import PlayerMatch
from utils.utils import *
from typing import List

class TeamMatch:
    def __init__(self, playerMatches: List[PlayerMatch], teamMatchId: int, datePlayed: str):
        self.playerMatches = playerMatches
        self.teamMatchId = teamMatchId
        self.datePlayed = datePlayed

    def getPlayerMatches(self):
        return self.playerMatches
    
    def getTeamMatchId(self):
        return self.teamMatchId
    
    def getDatePlayed(self):
        return self.datePlayed
    
    def getWinningTeams(self):
        team1, team2 = list(map(lambda playerResult: playerResult.getTeam(), self.playerMatches[0].getPlayerResults()))
        team1Pts = 0
        team2Pts = 0
        for playerMatch in self.playerMatches:
            playerResult1, playerResult2 = playerMatch.getPlayerResults()
            
            if playerResult1.getTeam() == team1:
                team1Pts += playerResult1.getScore().getTeamPtsEarned()
                team2Pts += playerResult2.getScore().getTeamPtsEarned()
            else:
                team1Pts += playerResult2.getScore().getTeamPtsEarned()
                team2Pts += playerResult1.getScore().getTeamPtsEarned()
        
        if team1Pts > team2Pts:
            return [team1]
        elif team1Pts == team2Pts:
            return [team1, team2]
        else:
            return [team2]