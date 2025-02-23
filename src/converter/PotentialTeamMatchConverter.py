from dataClasses.PlayerMatch import PlayerMatch
from src.dataClasses.PlayerMatch import PlayerMatch
from dataClasses.TeamMatch import TeamMatch
from dataClasses.PotentialTeamMatch import PotentialTeamMatch
from dataClasses.PotentialPlayerMatch import PotentialPlayerMatch
from utils.asl import *
from utils.utils import *
import math
from dataClasses.PotentialPlayerResult import PotentialPlayerResult

class PotentialTeamMatchConverter:
    def __init__(self):
        pass
    
    def toPotentialTeamMatchFromTeamMatch(self, teamMatch: TeamMatch, skillLevelMatrix):
        potentialPlayerMatches = []
        for playerMatch in teamMatch.getPlayerMatches():
            potentialPlayerMatch = self.toPotentialPlayerMatchFromPlayerMatch(playerMatch, skillLevelMatrix)
            potentialPlayerMatches.append(potentialPlayerMatch)

        return PotentialTeamMatch(potentialPlayerMatches)
    
    def toPotentialPlayerMatchFromPlayerMatch(self, playerMatch: PlayerMatch, skillLevelMatrix):
        potentialPlayerResults = []
        playerResults = playerMatch.getPlayerResults()
        player1 = playerResults[0].getPlayer()
        player2 = playerResults[1].getPlayer()
        team1 = playerResults[0].getTeam()
        team2 = playerResults[1].getTeam()

        player1.setAdjustedSkillLevel(getAdjustedSkillLevel(player1.getMemberId(), player1.getCurrentSkillLevel(), None, None))
        player2.setAdjustedSkillLevel(getAdjustedSkillLevel(player2.getMemberId(), player2.getCurrentSkillLevel(), None, None))
        asl1 = float(player1.getAdjustedSkillLevel())
        asl2 = float(player2.getAdjustedSkillLevel())

        # TODO: Refactor to be able to use the getExpectedPts method. This is all duplicated code #######
        rangeStart = getRangeStart("8-ball")
        
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
        expectedPts = (skillLevelMatrix[index1][index2], skillLevelMatrix[index2][index1])
        #################################################################################################


        potentialPlayerResults.append(PotentialPlayerResult(player1, team1, expectedPts[0]))
        potentialPlayerResults.append(PotentialPlayerResult(player2, team2, expectedPts[1]))
        
        return PotentialPlayerMatch(potentialPlayerResults)
        