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
    def __init__(self, myTeam: Team, opponentTeam: Team, putupPlayer: Player | None, matchIndex: int, format: Format):
        self.myTeam = myTeam
        self.opponentTeam = opponentTeam
        self.doesMyTeamPutUp = putupPlayer is None
        self.putupPlayer = putupPlayer
        self.matchIndex = matchIndex
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
        
    
    def start(self, teamMatchCriteria: TeamMatchCriteria, matchIndex: int) -> PotentialTeamMatch:
        startTime = time.perf_counter()
        self.myTeam.getPlayers().sort()
        self.opponentTeam.getPlayers().sort()
        throwIndexAddition = 0 if self.putupPlayer is None else 1
        throwIndex = (matchIndex * 2) + throwIndexAddition
        matchups = self.asynchronousAlgorithm(self.putupPlayer, teamMatchCriteria, throwIndex, self.myTeam.getPlayers(), self.opponentTeam.getPlayers(), PotentialTeamMatch([]), throwIndex)
        endTime = time.perf_counter()
        self.timeCounter[self.start.__name__] += endTime - startTime
        print(self.timeCounter)
        return matchups
    
    def getThrowIndexAddition(self, putupPlayer: Player | None):
        return 0 if putupPlayer is None else 1
    

    def asynchronousAlgorithm(self, putupPlayer: Player | None, teamMatchCriteria: TeamMatchCriteria, throwIndex: int, myPlayers: List[Player], theirPlayers: List[Player], soFarMatch: PotentialTeamMatch, originalThrowIndex: int) -> PotentialTeamMatch:
        # Base case: 5 PlayerMatches have been decided
        matchIndex = throwIndex // 2
        if matchIndex >= NUM_PLAYERMATCHES_IN_TEAMMATCH:
            return soFarMatch
        
        amILookingAtMyOwnTeam = self.myTeam.isPlayerOnTeam(myPlayers[0])
        bestMatch = None
        bestPlayer = None
        nextPutupPlayer = None
        tempMyPlayers = myPlayers.copy()
        tempTheirPlayers = theirPlayers.copy()
        nextMyPlayers = None
        nextTheirPlayers = None

        # The team with the "myPlayers" roster is throwing first. Loop through players for which one gives you the best score throughout the whole TeamMatch
        if putupPlayer is None:
            
            for player in self.findEligiblePlayers(tempMyPlayers, throwIndex, teamMatchCriteria, amILookingAtMyOwnTeam, throwIndex, soFarMatch):
                anotherTempMyPlayers = tempMyPlayers.copy()
                anotherTempMyPlayers.remove(player)
                anotherTempTheirPlayers = tempTheirPlayers.copy()
                potentialTeamMatch = self.findBestNextMatchup(player, anotherTempTheirPlayers, anotherTempMyPlayers, soFarMatch, teamMatchCriteria, throwIndex + 1, originalThrowIndex)
                if bestMatch is None or round(potentialTeamMatch.pointDifference(amILookingAtMyOwnTeam), 1) > round(bestMatch.pointDifference(amILookingAtMyOwnTeam), 1):
                    bestMatch = potentialTeamMatch
                    bestPlayer = player
                    
            tempMyPlayers.remove(bestPlayer)
            nextPutupPlayer = bestPlayer
            nextMyPlayers = tempTheirPlayers
            nextTheirPlayers = tempMyPlayers
        
        # The team with the "myPlayers" roster is responding to a throw
        else:
            unrealisticTeamMatch = self.findBestNextMatchup(putupPlayer, tempMyPlayers, tempTheirPlayers, soFarMatch, teamMatchCriteria, throwIndex, originalThrowIndex)
            firstPotentialPlayerMatch = unrealisticTeamMatch.getPotentialPlayerMatches()[len(soFarMatch.getPotentialPlayerMatches())]
            playerResult1, playerResult2 = firstPotentialPlayerMatch.getPotentialPlayerResults()
            soFarMatch.addPotentialPlayerResult(playerResult1)
            soFarMatch.addPotentialPlayerResult(playerResult2)
            
            # TODO: FIX THIS SECTION. It doesn't know which player is on which team. Probably use an if statment involving a combination of self.myTeam.getPlayers() and amILookinngAtMyOwnTeam

            player1 = playerResult1.getPlayer() 
            player2 = playerResult2.getPlayer()
            if amILookingAtMyOwnTeam:
                if player1 in self.myTeam.getPlayers():
                    bestPlayer = player1
                else:
                    bestPlayer = player2
            else:
                if player1 in self.myTeam.getPlayers():
                    bestPlayer = player2
                else:
                    bestPlayer = player1
            
            tempMyPlayers.remove(bestPlayer)
            nextPutupPlayer = None
            nextMyPlayers = tempMyPlayers
            nextTheirPlayers = tempTheirPlayers
            
        
        
        return self.asynchronousAlgorithm(nextPutupPlayer, teamMatchCriteria, throwIndex + 1, nextMyPlayers, nextTheirPlayers, soFarMatch, originalThrowIndex + 1)
        

    
    def findBestNextMatchup(self, putupPlayer: Player | None, myPlayers: List[Player], theirPlayers: List[Player], potentialTeamMatch: PotentialTeamMatch, teamMatchCriteria: TeamMatchCriteria, throwIndex: int, originalThrowIndex: int) -> PotentialTeamMatch:
        
        # This function is used to find the matchup that would happen for match index <throwIndex // 2>
        # The rest of the matchups that are generated from this function do not take into account teamMatchCriteria
        # because the opponent doesn't know the other team's order and only knows who can play that very match
        
        amILookingAtMyOwnTeam = self.myTeam.isPlayerOnTeam(myPlayers[0])
        matchIndex = throwIndex // 2

        bestPotentialTeamMatch = None
        for player in self.findEligiblePlayers(myPlayers, throwIndex, teamMatchCriteria, amILookingAtMyOwnTeam, originalThrowIndex, potentialTeamMatch):
            # Make copies of myPlayers, theirPlayers, and potentialTeamMatch
            tempMyPlayers, tempTheirPlayers, tempPotentialTeamMatch = self.makeCopies(player, myPlayers, theirPlayers, potentialTeamMatch)
            
            # If you don't throw first for this PlayerMatch, add the potential matchup to the potentialTeamMatch
            if putupPlayer is not None:
                self.addPlayerMatch(player, putupPlayer, tempPotentialTeamMatch)

            if matchIndex < NUM_PLAYERMATCHES_IN_TEAMMATCH - 1 or putupPlayer is None:
                tempPotentialTeamMatch = (
                    self.findBestNextMatchup(None, tempTheirPlayers, tempMyPlayers, tempPotentialTeamMatch, teamMatchCriteria, throwIndex + 1, originalThrowIndex)
                    if putupPlayer is not None 
                    else self.findBestNextMatchup(player, tempTheirPlayers, tempMyPlayers, tempPotentialTeamMatch, teamMatchCriteria, throwIndex + 1, originalThrowIndex)
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
    
    def findEligiblePlayers(self, players: List[Player], throwIndex: int, teamMatchCriteria: TeamMatchCriteria, amILookingAtMyOwnTeam: bool, originalThrowIndex: int, soFarMatch: PotentialTeamMatch) -> List[Player]:
        startTime = time.perf_counter()
        numUniquePlayersFromStart = self.getNumUniquePlayers(players, soFarMatch, amILookingAtMyOwnTeam)
        
        needToCheckTeamMatchCriteria = throwIndex == originalThrowIndex or not amILookingAtMyOwnTeam
        
        eligiblePlayers = []
        matchIndex = throwIndex // 2
        for player in players:
            skilLevelCapStartTime = time.perf_counter()
            if needToCheckTeamMatchCriteria and teamMatchCriteria.playerMustPlay(player, matchIndex, numUniquePlayersFromStart):
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
            numMatchesLeftAfterChoosingPlayer =  NUM_PLAYERMATCHES_IN_TEAMMATCH - matchIndex - 1
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
            passesTeamMatchCriteriaCheck = player.getMemberId() not in teamMatchCriteria.getMemberIdsForGame(matchIndex)
            if (
                not wouldExceedSkillLevelCap and 
                not wouldBreakDuplicateConstraint and
                (not needToCheckTeamMatchCriteria or (needToCheckTeamMatchCriteria and passesTeamMatchCriteriaCheck))
            ):
                eligiblePlayers.append(player)
        
        endTime = time.perf_counter()
        self.timeCounter[self.findEligiblePlayers.__name__] += endTime - startTime
        return eligiblePlayers
    
    def validate(self) -> None:
        if self.putupPlayer is not None and self.putupPlayer in self.opponentTeam.getPlayers():
            raise InvalidTeamMatchCriteria(f"ERROR: {self.putupPlayer.getPlayerName()} was just put up. They cannot also be selected from the list")

        myTeamCorrectNumPlayers = NUM_PLAYERMATCHES_IN_TEAMMATCH - self.matchIndex
        opponentTeamCorrectNumPlayers = NUM_PLAYERMATCHES_IN_TEAMMATCH - self.matchIndex if self.putupPlayer is None else NUM_PLAYERMATCHES_IN_TEAMMATCH - self.matchIndex - 1
        
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
