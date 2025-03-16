from dataClasses.Team import Team
from utils.asl import *
from utils.aslMatrix import *
from utils.utils import *
import math
from dataClasses.PotentialPlayerResult import PotentialPlayerResult
from dataClasses.PotentialTeamMatch import PotentialTeamMatch
from dataClasses.Player import Player
from src.dataClasses.TeamMatchCriteria import TeamMatchCriteria
from src.exceptions.InvalidTeamMatchCriteria import InvalidTeamMatchCriteria
from dataClasses.Team import Team
from typing import Tuple
from typing import List
import time
from srcMain.Config import Config
from srcMain.Typechecked import Typechecked

class TeamMatchup(Typechecked):
    def __init__(self, myTeam: Team, opponentTeam: Team, putupPlayer: Player | None, matchNumber: int, format: Format):
        self.myTeam = myTeam
        self.opponentTeam = opponentTeam
        self.doesMyTeamPutUp = putupPlayer is None
        self.putupPlayer = putupPlayer
        self.matchNumber = matchNumber
        self.format = format
        self.timeCounter = {
            self.start.__name__: 0,
            'removeDuplicatePlayersExceptLowest': 0,
            self.findEligiblePlayers.__name__: 0,
            'skillLevelCap': 0,
            'doublePlay': 0,
            self.getExpectedPts.__name__: 0,
            self.makeCopies.__name__: 0,
            "pointDifference": 0,
            "async0": 0,
            "async1": 0,
            "async2": 0,
            "async3": 0,
            "async4": 0,
        }
        self.config = Config().getConfig()
        
        self.validate()

        if self.format.value == Format.EIGHT_BALL.value:
            if self.putupPlayer is not None:
                self.putupPlayer.setAdjustedSkillLevel(getAdjustedSkillLevel(putupPlayer.getMemberId(), putupPlayer.getCurrentSkillLevel(), None))

            for player in self.myTeam.getPlayers():
                player.setAdjustedSkillLevel(getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None))

            for player in self.opponentTeam.getPlayers():
                player.setAdjustedSkillLevel(getAdjustedSkillLevel(player.getMemberId(), player.getCurrentSkillLevel(), None))
            
        self.skillLevelMatrix = createASLMatrix(self.format, self.config.get("predictionAccuracy").get("expectedPtsMethod"))
    
    def start(self, teamMatchCriteria: TeamMatchCriteria, matchNumber: int) -> PotentialTeamMatch:
        startTime = time.perf_counter()
        self.myTeam.getPlayers().sort()
        self.opponentTeam.getPlayers().sort()
        matchups = self.asynchronousAlgorithm(self.putupPlayer, teamMatchCriteria, matchNumber, self.myTeam.getPlayers(), self.opponentTeam.getPlayers(), PotentialTeamMatch([]))
        endTime = time.perf_counter()
        self.timeCounter[self.start.__name__] += endTime - startTime
        print(self.timeCounter)
        return matchups
    

    def asynchronousAlgorithm(self, putupPlayer: Player | None, teamMatchCriteria: TeamMatchCriteria, matchNumber: int, myPlayers: List[Player], theirPlayers: List[Player], soFarMatch: PotentialTeamMatch) -> PotentialTeamMatch:
        # print("asynchronousAlgorithm matchNumber: ", matchNumber)
        if matchNumber >= NUM_PLAYERMATCHES_IN_TEAMMATCH:
            return soFarMatch
        
        amILookingAtMyOwnTeam = self.myTeam.isPlayerOnTeam(myPlayers[0])
        
        bestMatch = None
        tempMyPlayers = myPlayers.copy()
        tempTheirPlayers = theirPlayers.copy()

        if amILookingAtMyOwnTeam and putupPlayer is None:
            # It's our team's throw first
            for player in self.findEligiblePlayers(tempMyPlayers, matchNumber, teamMatchCriteria, amILookingAtMyOwnTeam, matchNumber, soFarMatch):
                anotherTempMyPlayers = tempMyPlayers.copy()
                anotherTempMyPlayers.remove(player)
                anotherTempTheirPlayers = tempTheirPlayers.copy()
                potentialTeamMatch = self.asynchronousAlgorithm(player, teamMatchCriteria, matchNumber, anotherTempTheirPlayers, anotherTempMyPlayers, soFarMatch)
                if bestMatch is None or round(potentialTeamMatch.pointDifference(amILookingAtMyOwnTeam), 1) > round(bestMatch.pointDifference(amILookingAtMyOwnTeam), 1):
                    bestMatch = potentialTeamMatch
        else:
            startTime = time.perf_counter()
            unrealisticTeamMatch = self.findBestNextMatchup(putupPlayer, tempMyPlayers, tempTheirPlayers, soFarMatch, teamMatchCriteria, matchNumber, matchNumber)
            endTime = time.perf_counter()
            self.timeCounter[f"async{matchNumber}"] += endTime - startTime
            firstPotentialPlayerMatch = unrealisticTeamMatch.getPotentialPlayerMatches()[len(soFarMatch.getPotentialPlayerMatches())]
            playerResult1, playerResult2 = firstPotentialPlayerMatch.getPotentialPlayerResults()
            tempSoFarMatch = soFarMatch.copy()
            tempSoFarMatch.addPotentialPlayerResult(playerResult1)
            tempSoFarMatch.addPotentialPlayerResult(playerResult2)
            
            # TODO: FIX THIS SECTION. It doesn't know which player is on which team. Probably use an if statment involving a combination of self.myTeam.getPlayers() and amILookinngAtMyOwnTeam
            myPlayer = None
            theirPlayer = None
            player1 = playerResult1.getPlayer() 
            player2 = playerResult2.getPlayer()
            if amILookingAtMyOwnTeam:
                if player1 in self.myTeam.getPlayers():
                    myPlayer = player1
                    theirPlayer = player2
                else:
                    myPlayer = player2
                    theirPlayer = player1
            else:
                if player1 in self.myTeam.getPlayers():
                    myPlayer = player2
                    theirPlayer = player1
                else:
                    myPlayer = player1
                    theirPlayer = player2

            
            tempMyPlayers.remove(myPlayer)
            if putupPlayer is None:
                tempTheirPlayers.remove(theirPlayer)
                bestMatch = self.asynchronousAlgorithm(None, teamMatchCriteria, matchNumber + 1, tempTheirPlayers, tempMyPlayers, tempSoFarMatch)
            else:
                bestMatch = self.asynchronousAlgorithm(None, teamMatchCriteria, matchNumber + 1, tempMyPlayers, tempTheirPlayers, tempSoFarMatch)
            # bestMatch = bestMatch
        return bestMatch

    
    def findBestNextMatchup(self, chosenPlayer: Player | None, myPlayers: List[Player], theirPlayers: List[Player], potentialTeamMatch: PotentialTeamMatch, teamMatchCriteria: TeamMatchCriteria, matchNumber: int, originalMatchNumber: int) -> PotentialTeamMatch:
        # print("findBestNextMatchup matchNumber: ", matchNumber)
        # This function is used to find the matchup that would happen for match number <matchNumber>
        # The rest of the matchups that are generated from this function do not take into account teamMatchCriteria
        # because the opponent doesn't know the other team's order and only knows who can play that very match
        
        amILookingAtMyOwnTeam = self.myTeam.isPlayerOnTeam(myPlayers[0])

        bestPotentialTeamMatch = None
        for player in self.findEligiblePlayers(myPlayers, matchNumber, teamMatchCriteria, amILookingAtMyOwnTeam, originalMatchNumber, potentialTeamMatch):
            # Make copies of myPlayers, theirPlayers, and potentialTeamMatch
            tempMyPlayers, tempTheirPlayers, tempPotentialTeamMatch = self.makeCopies(player, myPlayers, theirPlayers, potentialTeamMatch)
            
            # If you don't throw first for this PlayerMatch, add the potential matchup to the potentialTeamMatch
            if chosenPlayer is not None:
                self.addPlayerMatch(player, chosenPlayer, tempPotentialTeamMatch)

            if matchNumber < NUM_PLAYERMATCHES_IN_TEAMMATCH - 1 or chosenPlayer is None:
                tempPotentialTeamMatch = (
                    self.findBestNextMatchup(None, tempTheirPlayers, tempMyPlayers, tempPotentialTeamMatch, teamMatchCriteria, matchNumber + 1, originalMatchNumber)
                    if chosenPlayer is not None 
                    else self.findBestNextMatchup(player, tempTheirPlayers, tempMyPlayers, tempPotentialTeamMatch, teamMatchCriteria, matchNumber, originalMatchNumber)
                )
            
            startTime = time.perf_counter()
            if bestPotentialTeamMatch is None or round(tempPotentialTeamMatch.pointDifference(amILookingAtMyOwnTeam), 1) > round(bestPotentialTeamMatch.pointDifference(amILookingAtMyOwnTeam), 1):
                bestPotentialTeamMatch = tempPotentialTeamMatch
            endTime = time.perf_counter()
            self.timeCounter["pointDifference"] += endTime - startTime
        
        return bestPotentialTeamMatch

    def getExpectedPts(self, player1: Player, player2: Player) -> Tuple[float, float]:
        startTime = time.perf_counter()
        
        asl1 = float(player1.getAdjustedSkillLevel())
        asl2 = float(player2.getAdjustedSkillLevel())

        skillLevelRange = getSkillLevelRangeForFormat(self.format)
        
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
        expectedPts = (self.skillLevelMatrix[index1][index2], self.skillLevelMatrix[index2][index1])
        
        endTime = time.perf_counter()
        self.timeCounter[self.getExpectedPts.__name__] += endTime - startTime

        return expectedPts

    def addPlayerMatch(self, player: Player, chosenPlayer: Player, newPotentialTeamMatch: PotentialTeamMatch) -> None:
        myPoints, theirPoints = self.getExpectedPts(player, chosenPlayer)
        if self.myTeam.isPlayerOnTeam(player):
            newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(player, self.myTeam, myPoints))
            newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(chosenPlayer, self.opponentTeam, theirPoints))
        else:
            newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(chosenPlayer, self.myTeam, theirPoints))
            newPotentialTeamMatch.addPotentialPlayerResult(PotentialPlayerResult(player, self.opponentTeam, myPoints))

    def makeCopies(self, player: Player, myPlayers: List[Player], theirPlayers: List[Player], potentialTeamMatch: PotentialTeamMatch) -> Tuple[List[Player], List[Player], PotentialTeamMatch]:
        startTime = time.perf_counter()
        tempMyPlayers = myPlayers.copy()
        tempMyPlayers.remove(player)
        tempTheirPlayers = theirPlayers.copy()
        tempPotentialTeamMatch = potentialTeamMatch.copy()
        endTime = time.perf_counter()
        self.timeCounter[self.makeCopies.__name__] += endTime - startTime
        return (tempMyPlayers, tempTheirPlayers, tempPotentialTeamMatch)
    
    def getNumUniquePlayers(self, players: List[Player], soFarMatch: PotentialTeamMatch, amILookingAtMyOwnTeam: bool) -> int:
        allPlayers = players + soFarMatch.getPlayers(amILookingAtMyOwnTeam)
        allMemberIds = list(map(lambda player: player.getMemberId(), allPlayers))
        return len(set(allMemberIds))
    
    def findEligiblePlayers(self, players: List[Player], matchNumber: int, teamMatchCriteria: TeamMatchCriteria, amILookingAtMyOwnTeam: bool, originalMatchNumber: int, soFarMatch: PotentialTeamMatch) -> List[Player]:
        startTime = time.perf_counter()
        numUniquePlayersFromStart = self.getNumUniquePlayers(players, soFarMatch, amILookingAtMyOwnTeam)
        
        noNeedToCheckTeamMatchCriteria = amILookingAtMyOwnTeam and matchNumber != originalMatchNumber
        
        eligiblePlayers = []
        for player in players:
            skilLevelCapStartTime = time.perf_counter()
            if not noNeedToCheckTeamMatchCriteria and teamMatchCriteria.playerMustPlay(player, matchNumber, numUniquePlayersFromStart):
                return [player]

            # Determine whether throwing that player would violate (or lead to a violation of) the 23 skill level cap rule
            

            playersCopy = players.copy()
            removeStartTime = time.perf_counter()
            
            # Find out how many duplicate plays you have left including selecting the consideredPlayer to play
            # Sort players based on skill level first
            # Iterate through each player. Whenever you come across a duplicate (same as previous player), increment the duplicateCount variable
            # As soon as the duplicateCount variable hits the same number as the number of duplicated plays allowed, go through the rest of the players and remove the remaining duplicates
            playersWhoHavePlayedSoFarIncludingThrowingPlayer = soFarMatch.getPlayers(amILookingAtMyOwnTeam) + [player]
            numDuplicatePlaysSoFarIncludingThrowingPlayer = len(playersWhoHavePlayedSoFarIncludingThrowingPlayer) - len(set(list(map(lambda currentPlayer: currentPlayer.getMemberId(), playersWhoHavePlayedSoFarIncludingThrowingPlayer))))
            numDuplicatePlaysAllowed = 0 if numUniquePlayersFromStart >= NUM_PLAYERMATCHES_IN_TEAMMATCH else NUM_PLAYERMATCHES_IN_TEAMMATCH - numUniquePlayersFromStart
            playersCopy.remove(player)
            remainingSkillLevels = []
            if len(playersCopy) < 2:
                remainingSkillLevels = playersCopy
            for index, currentPlayer in enumerate(playersCopy):
                if ((index == 0 and currentPlayer in playersWhoHavePlayedSoFarIncludingThrowingPlayer) or
                    currentPlayer == playersCopy[index - 1] or 
                    currentPlayer in playersWhoHavePlayedSoFarIncludingThrowingPlayer
                    ):
                    if numDuplicatePlaysSoFarIncludingThrowingPlayer >= numDuplicatePlaysAllowed:
                        continue
                    else:
                        numDuplicatePlaysSoFarIncludingThrowingPlayer += 1
                remainingSkillLevels.append(currentPlayer)

            removeEndTime = time.perf_counter()
            self.timeCounter['removeDuplicatePlayersExceptLowest'] += removeEndTime - removeStartTime
            numMatchesLeftAfterChoosingPlayer =  NUM_PLAYERMATCHES_IN_TEAMMATCH - matchNumber - 1
            sumRemainingSkillLevels = sum(list(map(lambda currentPlayer: currentPlayer.getCurrentSkillLevel(), remainingSkillLevels[:numMatchesLeftAfterChoosingPlayer])))
            sumSkillLevelsPlayedSoFar = soFarMatch.sumSkillLevels(amILookingAtMyOwnTeam)
            wouldExceedSkillLevelCap = sumRemainingSkillLevels + player.getCurrentSkillLevel() + sumSkillLevelsPlayedSoFar > SKILL_LEVEL_CAP
            skilLevelCapEndTime = time.perf_counter()
            self.timeCounter['skillLevelCap'] += skilLevelCapEndTime - skilLevelCapStartTime

            # Determine whether throwing that player would violate a double-play rule.
            # For example, if you only have 4 players, only one of them can double play
            doublePlayStartTime = time.perf_counter()
            playersWhoHavePlayedSoFarIncludingThrowingPlayer = soFarMatch.getPlayers(amILookingAtMyOwnTeam) + [player]
            numDuplicatePlaysSoFarIncludingThrowingPlayer = len(playersWhoHavePlayedSoFarIncludingThrowingPlayer) - len(set(list(map(lambda currentPlayer: currentPlayer.getMemberId(), playersWhoHavePlayedSoFarIncludingThrowingPlayer))))
            numDuplicatePlaysAllowed = 0 if numUniquePlayersFromStart >= NUM_PLAYERMATCHES_IN_TEAMMATCH else NUM_PLAYERMATCHES_IN_TEAMMATCH - numUniquePlayersFromStart
            wouldBreakDuplicateConstraint = numDuplicatePlaysSoFarIncludingThrowingPlayer > numDuplicatePlaysAllowed
            doublePlayEndTime = time.perf_counter()
            self.timeCounter['doublePlay'] += doublePlayEndTime - doublePlayStartTime

            # If we're deciding a putup an immediate next putup for our team, we need to check if the player is available that match
            # Otherwise, assume the opponent is making their decisions without knowledge of when our players are available
            passesTeamMatchCriteriaCheck = player.getMemberId() not in teamMatchCriteria.getMemberIdsForGame(matchNumber)
            if (
                not wouldExceedSkillLevelCap and 
                not wouldBreakDuplicateConstraint and
                (noNeedToCheckTeamMatchCriteria or (not noNeedToCheckTeamMatchCriteria and passesTeamMatchCriteriaCheck))
            ):
                eligiblePlayers.append(player)
        
        endTime = time.perf_counter()
        self.timeCounter[self.findEligiblePlayers.__name__] += endTime - startTime
        return eligiblePlayers
    
    def validate(self) -> None:
        if self.putupPlayer is not None and self.putupPlayer in self.opponentTeam.getPlayers():
            raise InvalidTeamMatchCriteria(f"ERROR: {self.putupPlayer.getPlayerName()} was just put up. They cannot also be selected from the list")

        myTeamCorrectNumPlayers = NUM_PLAYERMATCHES_IN_TEAMMATCH - self.matchNumber
        opponentTeamCorrectNumPlayers = NUM_PLAYERMATCHES_IN_TEAMMATCH - self.matchNumber if self.putupPlayer is None else NUM_PLAYERMATCHES_IN_TEAMMATCH - self.matchNumber - 1
        
        '''
        if len(self.myTeam.getPlayers()) != myTeamCorrectNumPlayers:
            raise InvalidTeamMatchCriteria(f"ERROR: Selected {len(self.myTeam.getPlayers())} players for {self.myTeam.getTeamName()}. Must select {myTeamCorrectNumPlayers} players")
        if len(self.opponentTeam.getPlayers()) != opponentTeamCorrectNumPlayers:
            raise InvalidTeamMatchCriteria(f"ERROR: Selected {len(self.opponentTeam.getPlayers())} players for {self.opponentTeam.getTeamName()}. Must select {opponentTeamCorrectNumPlayers} players")
        '''
        
        myTeamSkillLevelSum = sum(map(lambda player: player.getCurrentSkillLevel(), self.myTeam.getPlayers()))
        opponentTeamSkillLevelSum = sum(map(lambda player: player.getCurrentSkillLevel(), self.opponentTeam.getPlayers()))
        '''
        if myTeamSkillLevelSum > SKILL_LEVEL_CAP:
            raise InvalidTeamMatchCriteria(f"ERROR: selected players for {self.myTeam.getTeamName()} are over skill level cap by {myTeamSkillLevelSum - SKILL_LEVEL_CAP}")
        if opponentTeamSkillLevelSum > SKILL_LEVEL_CAP:
            raise InvalidTeamMatchCriteria(f"ERROR: selected players for {self.opponentTeam.getTeamName()} are over skill level cap by {opponentTeamSkillLevelSum - SKILL_LEVEL_CAP}")
        '''
