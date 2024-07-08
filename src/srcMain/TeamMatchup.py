from src.dataClasses.Team import Team
from utils.asl import *
from utils.utils import *
import math
import itertools
from src.dataClasses.Player import Player

class TeamMatchup():
    def __init__(self, myTeam: Team, opponentTeam: Team, doesMyTeamPutUp: bool):
        self.myTeam = myTeam
        self.opponentTeam = opponentTeam

        for player in self.myTeam.getPlayers():
            player.setAdjustedSkillLevel(getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None, None))

        for player in self.opponentTeam.getPlayers():
            player.setAdjustedSkillLevel(getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None, None))

        self.doesMyTeamPutUp = doesMyTeamPutUp
        # TODO: Remove hardcoded values
        self.game = "8-ball"
        self.skillLevelMatrix = createASLMatrix(self.game)

    def decideBestMatchups(self):
        bestMatchup = None
        maxPts = 0
        allMatchups = self.populateAllMatchups(self.myTeam.getPlayers(), self.opponentTeam.getPlayers())
        for matchup in allMatchups:
            expectedPts = 0
            for player1, player2 in matchup:
                expectedPts += self.getExpectedPts(player1, player2)
            if expectedPts > maxPts:
                maxPts = expectedPts
                bestMatchup = matchup

        bestMatchup = list(map(lambda pairing: (pairing[0].toJson(), pairing[1].toJson()), bestMatchup))
        print(self.getBestPutup())
        return (bestMatchup, maxPts)      
    
    def populateAllMatchups(self, roster1, roster2):
        uniqueCombinations = []
        perms = None
        reverse = len(roster2) > len(roster1)
        if reverse:
            perms = itertools.permutations(roster2, len(roster1))
        else:
            perms = itertools.permutations(roster1, len(roster2))
        for combination in perms:
            zipped = None
            if reverse:
                zipped = zip(combination, roster1)
            else:
                zipped = zip(combination, roster2)
            uniqueCombinations.append(list(zipped))
        
        if reverse:
            for innerIndex, uniqueCombination in enumerate(uniqueCombinations):
                for outerIndex, pairing in enumerate(uniqueCombination):
                    uniqueCombinations[innerIndex][outerIndex] = (pairing[1], pairing[0])
        return uniqueCombinations


    def getExpectedPts(self, player1, player2):
        asl1 = float(player1.getAdjustedSkillLevel())
        asl2 = float(player2.getAdjustedSkillLevel())

        rangeStart = getRangeStart(self.game)
        
        skillLevel1 = math.floor(asl1)
        asl1decimals = asl1 - skillLevel1
        asl1SectionIndex = 0
        for sectionIndex, section in enumerate(SECTIONS_PER_SKILL_LEVEL):
            if asl1decimals >= section[0] and asl1decimals < section[1]:
                asl1SectionIndex = sectionIndex
                break

        skillLevel2 = math.floor(asl2)
        asl2decimals = asl2 - skillLevel2
        asl2SectionIndex = 0
        for sectionIndex, section in enumerate(SECTIONS_PER_SKILL_LEVEL):
            if asl2decimals >= section[0] and asl2decimals < section[1]:
                asl2SectionIndex = sectionIndex
                break
        
        index1 = ((skillLevel1 - rangeStart) * NUM_SECTIONS_PER_SKILL_LEVEL) + asl1SectionIndex + 1 
        index2 = ((skillLevel2 - rangeStart) * NUM_SECTIONS_PER_SKILL_LEVEL) + asl2SectionIndex + 1 
        return self.skillLevelMatrix[index1][index2]
    
    def getBestPutup(self):
        bestExpectedPts = 0
        bestPlayers = []
        for player in self.myTeam.getPlayers():
            totalExpectedPts = 0
            allMatchups = self.populateAllMatchups([player], self.opponentTeam.getPlayers())
            
            for matchup in allMatchups:
                for player1, player2 in matchup:
                    totalExpectedPts += self.getExpectedPts(player1, player2)
                
            expectedPtsAvg = totalExpectedPts/len(allMatchups)
            if expectedPtsAvg > bestExpectedPts:
                bestExpectedPts = expectedPtsAvg
                bestPlayers = [player]
            elif bestExpectedPts == expectedPtsAvg:
                bestPlayers.append(player)
        return ((list(map(lambda player: player.toJson(), bestPlayers))), bestExpectedPts)

        



