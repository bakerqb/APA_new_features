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
    
    def asynchronousAlgorithm(self, putupPlayer: Player, teamMatchCriteria: TeamMatchCriteria, matchNumber: int, myPlayers: List[Player], theirPlayers: List[Player], soFarMatch: PotentialTeamMatch) -> PotentialTeamMatch:
        # print("asynchronousAlgorithm matchNumber: ", matchNumber)
        if matchNumber >= NUM_PLAYERMATCHES_IN_TEAMMATCH:
            return soFarMatch
        
        amILookingAtMyOwnTeam = self.myTeam.isPlayerOnTeam(myPlayers[0])
        tempSoFarMatch = soFarMatch.copy()
        bestMatch = None
        tempMyPlayers = myPlayers.copy()
        tempTheirPlayers = theirPlayers.copy()

        if amILookingAtMyOwnTeam and putupPlayer is None:
            # It's our team's throw first
            for player in self.findEligiblePlayers(tempMyPlayers, matchNumber, teamMatchCriteria, amILookingAtMyOwnTeam, matchNumber, tempSoFarMatch):
                anotherTempMyPlayers = tempMyPlayers.copy()
                anotherTempMyPlayers.remove(player)
                potentialTeamMatch = self.asynchronousAlgorithm(player, teamMatchCriteria, matchNumber, tempTheirPlayers, anotherTempMyPlayers, tempSoFarMatch)
                if bestMatch is None or potentialTeamMatch.pointDifference(amILookingAtMyOwnTeam) > bestMatch.pointDifference(amILookingAtMyOwnTeam):
                    bestMatch = potentialTeamMatch
        else:
            unrealisticTeamMatch = self.findBestNextMatchup(putupPlayer, tempMyPlayers, tempTheirPlayers, tempSoFarMatch, teamMatchCriteria, matchNumber, matchNumber)
            firstPotentialPlayerMatch = unrealisticTeamMatch.getPotentialPlayerMatches()[len(tempSoFarMatch.getPotentialPlayerMatches())]
            playerResult1, playerResult2 = firstPotentialPlayerMatch.getPotentialPlayerResults()
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

            if myPlayer in tempMyPlayers:  
                tempMyPlayers.remove(myPlayer)
            if theirPlayer in tempTheirPlayers:
                tempTheirPlayers.remove(theirPlayer)
            bestMatch = self.asynchronousAlgorithm(None, teamMatchCriteria, matchNumber + 1, tempTheirPlayers, tempMyPlayers, tempSoFarMatch)
            bestMatch = bestMatch
        return bestMatch

    def start(self, teamMatchCriteria: TeamMatchCriteria, matchNumber: int) -> PotentialTeamMatch:
        return self.asynchronousAlgorithm(self.putupPlayer, teamMatchCriteria, matchNumber, self.myTeam.getPlayers(), self.opponentTeam.getPlayers(), PotentialTeamMatch([]))

    
    def findBestNextMatchup(self, chosenPlayer: Player, myPlayers: List[Player], theirPlayers: List[Player], potentialTeamMatch: PotentialTeamMatch, teamMatchCriteria: TeamMatchCriteria, matchNumber: int, originalMatchNumber: int) -> PotentialTeamMatch:
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

            newPotentialTeamMatch = tempPotentialTeamMatch.copy()
            if matchNumber < NUM_PLAYERMATCHES_IN_TEAMMATCH - 1 or chosenPlayer is None:
                newPotentialTeamMatch = (
                    self.findBestNextMatchup(None, tempTheirPlayers, tempMyPlayers, tempPotentialTeamMatch, teamMatchCriteria, matchNumber + 1, originalMatchNumber)
                    if chosenPlayer is not None 
                    else self.findBestNextMatchup(player, tempTheirPlayers, tempMyPlayers, tempPotentialTeamMatch, teamMatchCriteria, matchNumber, originalMatchNumber)
                )
            
            if bestPotentialTeamMatch is None or newPotentialTeamMatch.pointDifference(amILookingAtMyOwnTeam) > bestPotentialTeamMatch.pointDifference(amILookingAtMyOwnTeam):
                bestPotentialTeamMatch = newPotentialTeamMatch.copy()
        
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
    
    def wouldThrowingPlayerExceedSkillLevelCap(self, player: Player, players: List[Player], matchNumber: int, soFarMatch: PotentialTeamMatch, amILookingAtMyOwnTeam: bool, numUniquePlayersFromStart: int):
        # Assuming you throw a player right now and then threw your weakest players for the rest of the match, this returns the sum of all their skill levels
        playersCopy = players.copy()
        # Make sure to remove any duplicate players when considering who else can play the rest of the match. For example, if you had 4 players to start the match, 2 players can't double play, only 1 can
        remainingSkillLevels = self.removeDuplicatePlayersExceptLowest(player, playersCopy, soFarMatch, amILookingAtMyOwnTeam, numUniquePlayersFromStart)
        numMatchesLeftAfterChoosingPlayer =  NUM_PLAYERMATCHES_IN_TEAMMATCH - matchNumber - 1
        sumRemainingSkillLevels = sum(list(map(lambda currentPlayer: currentPlayer.getCurrentSkillLevel(), remainingSkillLevels[:numMatchesLeftAfterChoosingPlayer])))
        sumSkillLevelsPlayedSoFar = soFarMatch.sumSkillLevels(amILookingAtMyOwnTeam)

        return sumRemainingSkillLevels + player.getCurrentSkillLevel() + sumSkillLevelsPlayedSoFar > SKILL_LEVEL_CAP
    
    def getNumUniquePlayers(self, players: List[Player], soFarMatch: PotentialTeamMatch, amILookingAtMyOwnTeam: bool):
        allPlayers = players + soFarMatch.getPlayers(amILookingAtMyOwnTeam)
        allMemberIds = list(map(lambda player: player.getMemberId(), allPlayers))
        return len(set(allMemberIds))
    
    def wouldThrowingPlayerBreakDuplicatePlayerConstraint(self, player: Player, soFarMatch: PotentialTeamMatch, amILookingAtMyOwnTeam: bool, numUniquePlayersFromStart: int):
        playersWhoHavePlayedSoFarIncludingThrowingPlayer = soFarMatch.getPlayers(amILookingAtMyOwnTeam) + [player]
        numDuplicatePlaysSoFarIncludingThrowingPlayer = len(playersWhoHavePlayedSoFarIncludingThrowingPlayer) - len(set(list(map(lambda currentPlayer: currentPlayer.getMemberId(), playersWhoHavePlayedSoFarIncludingThrowingPlayer))))
        numDuplicatePlaysAllowed = 0 if numUniquePlayersFromStart >= NUM_PLAYERMATCHES_IN_TEAMMATCH else NUM_PLAYERMATCHES_IN_TEAMMATCH - numUniquePlayersFromStart
        return numDuplicatePlaysSoFarIncludingThrowingPlayer > numDuplicatePlaysAllowed
            

    
    def removeDuplicatePlayersExceptLowest(self, player: Player, players: List[Player], soFarMatch: PotentialTeamMatch, amILookingAtMyOwnTeam: bool, numUniquePlayersFromStart: int):
        # Find out how many duplicate plays you have left including selecting the consideredPlayer to play
        # Sort players based on skill level first
        # Iterate through each player. Whenever you come across a duplicate (same as previous player), increment the duplicateCount variable
        # As soon as the duplicateCount variable hits the same number as the number of duplicated plays allowed, go through the rest of the players and remove the remaining duplicates
        playersWhoHavePlayedSoFarIncludingThrowingPlayer = soFarMatch.getPlayers(amILookingAtMyOwnTeam) + [player]
        numDuplicatePlaysSoFarIncludingThrowingPlayer = len(playersWhoHavePlayedSoFarIncludingThrowingPlayer) - len(set(list(map(lambda currentPlayer: currentPlayer.getMemberId(), playersWhoHavePlayedSoFarIncludingThrowingPlayer))))
        numDuplicatePlaysAllowed = 0 if numUniquePlayersFromStart >= NUM_PLAYERMATCHES_IN_TEAMMATCH else NUM_PLAYERMATCHES_IN_TEAMMATCH - numUniquePlayersFromStart
        playersCopy = players.copy()
        playersCopy.remove(player)
        playersCopy.sort()
        returnedPlayers = []
        if len(playersCopy) < 2:
            return playersCopy
        for index, player in enumerate(playersCopy):
            if player == playersCopy[index - 1] or player in playersWhoHavePlayedSoFarIncludingThrowingPlayer:
                if numDuplicatePlaysSoFarIncludingThrowingPlayer >= numDuplicatePlaysAllowed:
                    continue
                else:
                    numDuplicatePlaysSoFarIncludingThrowingPlayer += 1
            returnedPlayers.append(player)
        print("removeDuplicatePlayersExceptLowest")
        return returnedPlayers
    
    def findEligiblePlayers(self, players: List[Player], matchNumber: int, teamMatchCriteria: TeamMatchCriteria, amILookingAtMyOwnTeam: bool, originalMatchNumber: int, soFarMatch: PotentialTeamMatch):
        numUniquePlayersFromStart = self.getNumUniquePlayers(players, soFarMatch, amILookingAtMyOwnTeam)
        if amILookingAtMyOwnTeam and matchNumber != originalMatchNumber:
            eligiblePlayers = []
            for player in players:
                if (not self.wouldThrowingPlayerExceedSkillLevelCap(player, players, matchNumber, soFarMatch, amILookingAtMyOwnTeam, numUniquePlayersFromStart)
                    and not self.wouldThrowingPlayerBreakDuplicatePlayerConstraint(player, soFarMatch, amILookingAtMyOwnTeam, numUniquePlayersFromStart)):
                    eligiblePlayers.append(player)
            return eligiblePlayers
        
        eligiblePlayers = []
        for player in players:
            if (self.wouldThrowingPlayerExceedSkillLevelCap(player, players, matchNumber, soFarMatch, amILookingAtMyOwnTeam, numUniquePlayersFromStart)
                or self.wouldThrowingPlayerBreakDuplicatePlayerConstraint(player, soFarMatch, amILookingAtMyOwnTeam, numUniquePlayersFromStart)):
                continue
            '''
            if teamMatchCriteria.playerMustPlay(player, matchNumber):
                return [player]
            '''
            if player.getMemberId() not in teamMatchCriteria.getMemberIdsForGame(matchNumber):
                eligiblePlayers.append(player)
        return eligiblePlayers
    
    def validate(self):
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
