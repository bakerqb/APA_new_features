from dataClasses.PotentialPlayerMatch import PotentialPlayerMatch

class PotentialTeamMatch:
    def __init__(self, potentialPlayerMatches: list):
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
        return sum
    
    def toJson(self):
        return {
            "potentialPlayerMatches": list(map(lambda potentialPlayerMatch: potentialPlayerMatch.toJson(), self.potentialPlayerMatches))
        }
    
    def copy(self):
        tempPotentialPlayerMatches = self.potentialPlayerMatches.copy()
        return PotentialTeamMatch(tempPotentialPlayerMatches)
    
    def reversePotentialPlayerMatches(self):
        self.potentialPlayerMatches = list(reversed(self.potentialPlayerMatches))

    
    