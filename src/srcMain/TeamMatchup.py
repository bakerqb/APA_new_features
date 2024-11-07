from src.dataClasses.Team import Team
from utils.asl import *
from utils.utils import *
import math
from src.dataClasses.PotentialPlayerResult import PotentialPlayerResult
from src.dataClasses.PotentialTeamMatch import PotentialTeamMatch
from src.dataClasses.Player import Player
from src.dataClasses.TeamMatchCriteria import TeamMatchCriteria
from src.exceptions.InvalidTeamMatchCriteria import InvalidTeamMatchCriteria
from typing import Tuple
from typing import List

class TeamMatchup():
    def __init__(self, myTeam: Team, opponentTeam: Team, putupPlayer: Player, matchNumber: int):
        self.myTeam = myTeam
        self.opponentTeam = opponentTeam
        self.doesMyTeamPutUp = putupPlayer is None
        self.putupPlayer = putupPlayer
        self.matchNumber = matchNumber
        
        self.validate()

        if self.putupPlayer is not None:
            self.putupPlayer.setAdjustedSkillLevel(getAdjustedSkillLevel(putupPlayer.getMemberId(), putupPlayer.getCurrentSkillLevel(), None, None))

        for player in self.myTeam.getPlayers():
            player.setAdjustedSkillLevel(getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None, None))

        for player in self.opponentTeam.getPlayers():
            player.setAdjustedSkillLevel(getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None, None))

        # TODO: Remove hardcoded values
        self.game = "8-ball"
        self.skillLevelMatrix = createASLMatrix(self.game)

    def getExpectedPts(self, player1: Player, player2: Player) -> Tuple[int]:
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
    
    def start(self, teamMatchCriteria: TeamMatchCriteria, matchNumber: int) -> PotentialTeamMatch:
        return self.putup(self.putupPlayer, self.myTeam.getPlayers(), self.opponentTeam.getPlayers(), PotentialTeamMatch([]), teamMatchCriteria, matchNumber)    
    
    def putup(self, chosenPlayer: Player, myPlayers: List[Player], theirPlayers: List[Player], potentialTeamMatch: PotentialTeamMatch, teamMatchCriteria: TeamMatchCriteria, matchNumber: int) -> PotentialTeamMatch:
        amILookingAtMyOwnTeam = self.myTeam.isPlayerOnTeam(myPlayers[0])

        bestPotentialTeamMatch = None
        for player in self.findEligiblePlayers(myPlayers, matchNumber, teamMatchCriteria):
            # Make copies of myPlayers, theirPlayers, and potentialTeamMatch
            tempMyPlayers, tempTheirPlayers, tempPotentialTeamMatch = self.makeCopies(player, myPlayers, theirPlayers, potentialTeamMatch)
            
            # If you don't throw first for this PlayerMatch, add the potential matchup to the potentialTeamMatch
            if chosenPlayer is not None:
                self.addPlayerMatch(player, chosenPlayer, tempPotentialTeamMatch)

            newPotentialTeamMatch = tempPotentialTeamMatch
            if matchNumber < NUM_PLAYERMATCHES_IN_TEAMMATCH - 1 or chosenPlayer is None:
                newPotentialTeamMatch = (
                    self.putup(None, tempTheirPlayers, tempMyPlayers, tempPotentialTeamMatch, teamMatchCriteria, matchNumber + 1)
                    if chosenPlayer is not None 
                    else self.putup(player, tempTheirPlayers, tempMyPlayers, tempPotentialTeamMatch, teamMatchCriteria, matchNumber)
                )
            
            theirExpectedTotalPts = newPotentialTeamMatch.sumPoints(not amILookingAtMyOwnTeam)
            myExpectedTotalPts = newPotentialTeamMatch.sumPoints(amILookingAtMyOwnTeam)
            if amILookingAtMyOwnTeam:
                if bestPotentialTeamMatch is None or myExpectedTotalPts - theirExpectedTotalPts > bestPotentialTeamMatch.sumPoints(amILookingAtMyOwnTeam) - bestPotentialTeamMatch.sumPoints(not amILookingAtMyOwnTeam):
                    bestPotentialTeamMatch = newPotentialTeamMatch
            else:
                if bestPotentialTeamMatch is None or theirExpectedTotalPts - myExpectedTotalPts > bestPotentialTeamMatch.sumPoints(not amILookingAtMyOwnTeam) - bestPotentialTeamMatch.sumPoints(amILookingAtMyOwnTeam):
                    bestPotentialTeamMatch = newPotentialTeamMatch
        
        return bestPotentialTeamMatch

    def addPlayerMatch(self, player: Player, chosenPlayer: Player, newPotentialTeamMatch: PotentialTeamMatch):
        myPoints, theirPoints = self.getExpectedPts(player, chosenPlayer)
        if self.myTeam.isPlayerOnTeam(player):
            newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(player, myPoints))
            newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(chosenPlayer, theirPoints))
        else:
            newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(chosenPlayer, theirPoints))
            newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(player, myPoints))

    def makeCopies(self, player: Player, myPlayers: List[Player], theirPlayers: List[Player], potentialTeamMatch: PotentialTeamMatch):
        tempMyPlayers = myPlayers.copy()
        tempMyPlayers.remove(player)
        tempTheirPlayers = theirPlayers.copy()
        tempPotentialTeamMatch = potentialTeamMatch.copy()
        return (tempMyPlayers, tempTheirPlayers, tempPotentialTeamMatch)
    
    def findEligiblePlayers(self, players: List[Player], matchNumber: int, teamMatchCriteria: TeamMatchCriteria):
        eligiblePlayers = []
        for player in players:
            if teamMatchCriteria.playerMustPlay(player, matchNumber):
                return [player]
            if player.getMemberId() not in teamMatchCriteria.getMemberIdsForGame(matchNumber):
                eligiblePlayers.append(player)
        return eligiblePlayers
    
    def validate(self):
        if self.putupPlayer in self.opponentTeam.getPlayers():
            raise InvalidTeamMatchCriteria(f"ERROR: {self.putupPlayer.getPlayerName()} was just put up. They cannot also be selected from the list")

        myTeamCorrectNumPlayers = NUM_PLAYERMATCHES_IN_TEAMMATCH - self.matchNumber
        opponentTeamCorrectNumPlayers = NUM_PLAYERMATCHES_IN_TEAMMATCH - self.matchNumber if self.putupPlayer is None else NUM_PLAYERMATCHES_IN_TEAMMATCH - self.matchNumber - 1
        if len(self.myTeam.getPlayers()) != myTeamCorrectNumPlayers:
            raise InvalidTeamMatchCriteria(f"ERROR: Selected {len(self.myTeam.getPlayers())} players for {self.myTeam.getTeamName()}. Must select {myTeamCorrectNumPlayers} players")
        if len(self.opponentTeam.getPlayers()) != opponentTeamCorrectNumPlayers:
            raise InvalidTeamMatchCriteria(f"ERROR: Selected {len(self.opponentTeam.getPlayers())} players for {self.opponentTeam.getTeamName()}. Must select {opponentTeamCorrectNumPlayers} players")
        
        myTeamSkillLevelSum = sum(map(lambda player: player.getCurrentSkillLevel(), self.myTeam.getPlayers()))
        opponentTeamSkillLevelSum = sum(map(lambda player: player.getCurrentSkillLevel(), self.opponentTeam.getPlayers()))
        if myTeamSkillLevelSum > SKILL_LEVEL_CAP:
            raise InvalidTeamMatchCriteria(f"ERROR: selected players for {self.myTeam.getTeamName()} are over skill level cap by {myTeamSkillLevelSum - SKILL_LEVEL_CAP}")
        if opponentTeamSkillLevelSum > SKILL_LEVEL_CAP:
            raise InvalidTeamMatchCriteria(f"ERROR: selected players for {self.opponentTeam.getTeamName()} are over skill level cap by {opponentTeamSkillLevelSum - SKILL_LEVEL_CAP}")
