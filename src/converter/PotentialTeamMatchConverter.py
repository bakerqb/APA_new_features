from dataClasses.PlayerMatch import PlayerMatch
from dataClasses.TeamMatch import TeamMatch
from dataClasses.PotentialTeamMatch import PotentialTeamMatch
from dataClasses.PotentialPlayerMatch import PotentialPlayerMatch
from utils.utils import *
import math
from dataClasses.PotentialPlayerResult import PotentialPlayerResult
from src.srcMain.Typechecked import Typechecked

class PotentialTeamMatchConverter(Typechecked):
    def __init__(self):
        pass
    
    def toPotentialTeamMatchFromTeamMatch(self, teamMatch: TeamMatch, skillLevelMatrix, format: Format) -> PotentialTeamMatch:
        potentialPlayerMatches = []
        for playerMatch in teamMatch.getPlayerMatches():
            potentialPlayerMatch = self.toPotentialPlayerMatchFromPlayerMatch(playerMatch, skillLevelMatrix, format)
            potentialPlayerMatches.append(potentialPlayerMatch)

        return PotentialTeamMatch(potentialPlayerMatches)
    
    def toPotentialPlayerMatchFromPlayerMatch(self, playerMatch: PlayerMatch, skillLevelMatrix, format: Format) -> PotentialPlayerMatch:
        potentialPlayerResults = []
        playerResults = playerMatch.getPlayerResults()
        player1 = playerResults[0].getPlayer()
        player2 = playerResults[1].getPlayer()
        team1 = playerResults[0].getTeam()
        team2 = playerResults[1].getTeam()
        asl1 = playerResults[0].getAdjustedSkillLevel()
        asl2 = playerResults[1].getAdjustedSkillLevel()

        # TODO: Refactor to be able to use the getExpectedPts method. This is all duplicated code #######
        skillLevelRange = getSkillLevelRangeForFormat(format)
        
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
        
        index1 = ((skillLevel1 - skillLevelRange[0]) * NUM_SECTIONS_PER_SKILL_LEVEL) + asl1SectionIndex + 1 
        index2 = ((skillLevel2 - skillLevelRange[0]) * NUM_SECTIONS_PER_SKILL_LEVEL) + asl2SectionIndex + 1 
        expectedPts = (skillLevelMatrix[index1][index2], skillLevelMatrix[index2][index1])
        #################################################################################################


        potentialPlayerResults.append(PotentialPlayerResult(player1, team1, expectedPts[0]))
        potentialPlayerResults.append(PotentialPlayerResult(player2, team2, expectedPts[1]))
        
        return PotentialPlayerMatch(potentialPlayerResults)
        