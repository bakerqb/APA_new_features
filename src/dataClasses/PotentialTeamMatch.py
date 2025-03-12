from dataClasses.PotentialPlayerMatch import PotentialPlayerMatch
from dataClasses.PotentialPlayerResult import PotentialPlayerResult
from dataClasses.Player import Player
from dataClasses.Team import Team
from typing import List
from src.srcMain.Typechecked import Typechecked

class PotentialTeamMatch(Typechecked):
    def __init__(self, potentialPlayerMatches: List[PotentialPlayerMatch]):
        self.potentialPlayerMatches = potentialPlayerMatches

    def getPotentialPlayerMatches(self) -> List[PotentialPlayerMatch]:
        return self.potentialPlayerMatches
    
    def addPotentialPlayerResult(self, potentialPlayerResult: PotentialPlayerResult):
        if len(self.potentialPlayerMatches) == 0 or len(self.potentialPlayerMatches[-1].getPotentialPlayerResults()) == 2:
            potentialPlayerMatch = PotentialPlayerMatch([potentialPlayerResult])
            self.potentialPlayerMatches.append(potentialPlayerMatch)
        else:
            self.potentialPlayerMatches[-1].addPotentialPlayerResult(potentialPlayerResult)

    def sumPoints(self, isMyTeam: bool) -> float:
        sum = 0
        isMyTeamInt = 0 if isMyTeam else 1
        for potentialPlayerMatch in self.potentialPlayerMatches:
            sum += potentialPlayerMatch.getPotentialPlayerResults()[isMyTeamInt].getExpectedPts()
        return round(sum, 1)
    
    def sumSkillLevels(self, isMyTeam: bool) -> int:
        sum = 0
        isMyTeamInt = 0 if isMyTeam else 1
        for potentialPlayerMatch in self.potentialPlayerMatches:
            sum += potentialPlayerMatch.getPotentialPlayerResults()[isMyTeamInt].getPlayer().getCurrentSkillLevel()
        return sum
    
    def getPlayers(self, isMyTeam: bool) -> List[Player]:
        isMyTeamInt = 0 if isMyTeam else 1
        return list(map(lambda potentialPlayerMatch: potentialPlayerMatch.getPotentialPlayerResults()[isMyTeamInt].getPlayer(), self.potentialPlayerMatches))
            
 
    def copy(self):
        tempPotentialPlayerMatches = self.potentialPlayerMatches.copy()
        return PotentialTeamMatch(tempPotentialPlayerMatches)
    
    def pointDifference(self, isMyTeam: bool) -> float:
        theirExpectedTotalPts = self.sumPoints(False)
        myExpectedTotalPts = self.sumPoints(True)
        if isMyTeam:
            return myExpectedTotalPts - theirExpectedTotalPts
        else:
            return theirExpectedTotalPts - myExpectedTotalPts
        
    def getExpectedWinningTeams(self) -> List[Team]:
        myTeamPts = self.sumPoints(True)
        theirTeamPts = self.sumPoints(False)
        myTeam = self.potentialPlayerMatches[0].getPotentialPlayerResults()[0].getTeam()
        theirTeam = self.potentialPlayerMatches[0].getPotentialPlayerResults()[1].getTeam()
        if myTeamPts > theirTeamPts:
            return [myTeam]
        elif myTeamPts == theirTeamPts:
            return [myTeam, theirTeam]
        else:
            return [theirTeam]
