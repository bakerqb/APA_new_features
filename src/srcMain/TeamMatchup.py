from src.dataClasses.Team import Team
from utils.asl import *
from utils.utils import *
import math
from src.dataClasses.PotentialPlayerResult import PotentialPlayerResult
from src.dataClasses.PotentialTeamMatch import PotentialTeamMatch
from src.dataClasses.Player import Player
import sys

class TeamMatchup():
    def __init__(self, myTeam: Team, opponentTeam: Team, putupPlayer: Player):
        self.myTeam = myTeam
        self.opponentTeam = opponentTeam
        self.doesMyTeamPutUp = putupPlayer is None
        self.putupPlayer = putupPlayer

        if self.putupPlayer is not None:
            self.putupPlayer.setAdjustedSkillLevel(getAdjustedSkillLevel(putupPlayer.getMemberId(), putupPlayer.getCurrentSkillLevel(), None, None))

        for player in self.myTeam.getPlayers():
            player.setAdjustedSkillLevel(getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None, None))

        for player in self.opponentTeam.getPlayers():
            player.setAdjustedSkillLevel(getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None, None))

        # TODO: Remove hardcoded values
        self.game = "8-ball"
        self.skillLevelMatrix = createASLMatrix(self.game)

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
        return (self.skillLevelMatrix[index1][index2], self.skillLevelMatrix[index2][index1])
    
    def start(self):
        potentialTeamMatch = PotentialTeamMatch([])
        if self.doesMyTeamPutUp:
            potentialTeamMatch = self.putupBlind(self.myTeam.getPlayers(), self.opponentTeam.getPlayers(), potentialTeamMatch)

        else:
            potentialTeamMatch = self.putupNonBlind(self.putupPlayer, self.myTeam.getPlayers(), self.opponentTeam.getPlayers(), potentialTeamMatch)
        potentialTeamMatch.reversePotentialPlayerMatches()
        return potentialTeamMatch

    def putupBlind(self, myPlayers, theirPlayers, potentialTeamMatch):
        # Assert len(myPlayers) - 1 == len(theirPlayers)
        if len(myPlayers) == 1:
            myPlayer = myPlayers[0]
            theirPlayer = theirPlayers[0]
            myExpectedPts, theirExpectedPts = self.getExpectedPts(myPlayer, theirPlayer)
            if self.myTeam.isPlayerOnTeam(myPlayer):
                potentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(myPlayer, myExpectedPts))
                potentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(theirPlayer, theirExpectedPts))
            else:
                potentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(theirPlayer, theirExpectedPts))
                potentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(myPlayer, myExpectedPts))
            return potentialTeamMatch
        
        bestPotentialTeamMatch = None
        worstExpectedPtsForOpponents = (-1 * sys.maxsize, sys.maxsize)
        for player in myPlayers:
            # tell the other team who your theoretical putup is
            tempMyPlayers = myPlayers.copy()
            tempMyPlayers.remove(player)

            tempTheirPlayers = theirPlayers.copy()
            tempPotentialTeamMatch = potentialTeamMatch.copy()
            
            # Assume they go through each of their players and decide the best one to putup against you
            newPotentialTeamMatch = self.putupNonBlind(player, tempTheirPlayers, tempMyPlayers, tempPotentialTeamMatch)
            amILookingAtMyTeam = self.myTeam.isPlayerOnTeam(player)
            theirExpectedTotalPts = newPotentialTeamMatch.sumPoints(not amILookingAtMyTeam)
            myExpectedTotalPts = newPotentialTeamMatch.sumPoints(amILookingAtMyTeam)

            '''
            if len(self.opponentTeam.getPlayers()) == len(newPotentialTeamMatch.getPotentialPlayerMatches()):
                print(myExpectedTotalPts - theirExpectedTotalPts, "if we throw", player.getPlayerName())
            '''

            if theirExpectedTotalPts - myExpectedTotalPts < worstExpectedPtsForOpponents[1] - worstExpectedPtsForOpponents[0]:
                worstExpectedPtsForOpponents = (myExpectedTotalPts, theirExpectedTotalPts)
                bestPotentialTeamMatch = newPotentialTeamMatch
        
        # Pick player from your team where the opponent will get the lowest number of points
        
        return bestPotentialTeamMatch
                
    
    def putupNonBlind(self, chosenPlayer, myPlayers, theirPlayers, potentialTeamMatch):
        # Assert len(myPlayers) - 1 == len(theirPlayers)
        if len(myPlayers) == 1:
            myPlayer = myPlayers[0]
            theirPlayer = theirPlayers[0]
            myExpectedPts, theirExpectedPts = self.getExpectedPts(myPlayer, chosenPlayer)
            if self.myTeam.isPlayerOnTeam(myPlayer):
                potentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(myPlayer, myExpectedPts))
                potentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(theirPlayer, theirExpectedPts))
            else:
                potentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(theirPlayer, theirExpectedPts))
                potentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(myPlayer, myExpectedPts))
            return potentialTeamMatch
        
        bestPotentialTeamMatch = None
        bestPlayerExpectedPts = (-1 * sys.maxsize, sys.maxsize)
        for player in myPlayers:
            myPoints, theirPoints = self.getExpectedPts(player, chosenPlayer)
            tempMyPlayers = myPlayers.copy()
            tempMyPlayers.remove(player)
            tempTheirPlayers = theirPlayers.copy()
            tempPotentialTeamMatch = potentialTeamMatch.copy()
            newPotentialTeamMatch = self.putupBlind(tempMyPlayers, tempTheirPlayers, tempPotentialTeamMatch)
            amILookingAtMyOwnTeam = not self.myTeam.isPlayerOnTeam(chosenPlayer)
            theirExpectedTotalPts = theirPoints + newPotentialTeamMatch.sumPoints(not amILookingAtMyOwnTeam)
            myExpectedTotalPts = myPoints + newPotentialTeamMatch.sumPoints(amILookingAtMyOwnTeam)

            '''
            if chosenPlayer.getPlayerName() == "Patrick Barrett":
                print(myExpectedTotalPts - theirExpectedTotalPts, "if we throwww", player.getPlayerName())
            '''

            if myExpectedTotalPts - theirExpectedTotalPts > bestPlayerExpectedPts[0] - bestPlayerExpectedPts[1]:
                if self.myTeam.isPlayerOnTeam(player):
                    newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(player, myPoints))
                    newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(chosenPlayer, theirPoints))
                else:
                    newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(chosenPlayer, theirPoints))
                    newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(player, myPoints))
                
                bestPotentialTeamMatch = newPotentialTeamMatch
                bestPlayerExpectedPts = (myExpectedTotalPts, theirExpectedTotalPts)
            
        
        return bestPotentialTeamMatch
