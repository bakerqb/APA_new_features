from dataClasses.PotentialPlayerMatch import PotentialPlayerMatch
from dataClasses.Team import Team
from typing import List

class PotentialTeamMatch:
    def __init__(self, potentialPlayerMatches: List[PotentialPlayerMatch]):
        self.potentialPlayerMatches = potentialPlayerMatches

    def getPotentialPlayerMatches(self):
        return self.potentialPlayerMatches
    
    def addPotentialPlayerResult(self, potentialPlayerResult):
        if len(self.potentialPlayerMatches) == 0 or len(self.potentialPlayerMatches[-1].getPotentialPlayerResults()) == 2:
            potentialPlayerMatch = PotentialPlayerMatch([potentialPlayerResult])
            self.potentialPlayerMatches.append(potentialPlayerMatch)
        else:
            self.potentialPlayerMatches[-1].addPotentialPlayerResult(potentialPlayerResult)

    def sumPoints(self, isMyTeam):
        sum = 0
        isMyTeam = 0 if isMyTeam else 1
        for potentialPlayerMatch in self.potentialPlayerMatches:
            sum += potentialPlayerMatch.getPotentialPlayerResults()[isMyTeam].getExpectedPts()
        return round(sum, 1)
    
    def sumSkillLevels(self, isMyTeam):
        sum = 0
        isMyTeam = 0 if isMyTeam else 1
        for potentialPlayerMatch in self.potentialPlayerMatches:
            sum += potentialPlayerMatch.getPotentialPlayerResults()[isMyTeam].getPlayer().getCurrentSkillLevel()
        return sum
    
    def getPlayers(self, isMyTeam):
        isMyTeam = 0 if isMyTeam else 1
        return list(map(lambda potentialPlayerMatch: potentialPlayerMatch.getPotentialPlayerResults()[isMyTeam].getPlayer(), self.potentialPlayerMatches))
            
 
    def copy(self):
        tempPotentialPlayerMatches = self.potentialPlayerMatches.copy()
        return PotentialTeamMatch(tempPotentialPlayerMatches)
    
    def pointDifference(self, isMyTeam):
        theirExpectedTotalPts = self.sumPoints(False)
        myExpectedTotalPts = self.sumPoints(True)
        if isMyTeam:
            return myExpectedTotalPts - theirExpectedTotalPts
        else:
            return theirExpectedTotalPts - myExpectedTotalPts
        
    def getExpectedWinningTeams(self):
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
