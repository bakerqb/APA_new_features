from src.dataClasses.Player import Player
from utils.utils import *
from typing import List
from src.dataClasses.Team import Team
from src.exceptions.InvalidTeamMatchCriteria import InvalidTeamMatchCriteria

class TeamMatchCriteria:
    def __init__(self, teamMatchCriteriaRawInput: str, team1: Team, team2: Team, matchNumber: int, putupPlayer: Player):
        # Formatted as a list of list of ids, where the first element signifies which players cannot play in game 1
        self.idsForGames = []
        for i in range(NUM_PLAYERMATCHES_IN_TEAMMATCH):
            self.idsForGames.append(set())
        for criteria in teamMatchCriteriaRawInput:
            id, matchNumberTemp = criteria.split('-')
            self.idsForGames[int(matchNumberTemp)].add(int(id))
        
        self.validate(team1, team2, matchNumber, putupPlayer)


    def getMemberIdsForGame(self, gameIndex: int) -> List[int]:
        return self.idsForGames[gameIndex]
    
    def playerMustPlay(self, player: Player, matchIndex: int) -> bool:
        if player.getMemberId() in self.idsForGames[matchIndex]:
            return False
        if matchIndex == NUM_PLAYERMATCHES_IN_TEAMMATCH - 1:
            return True
        for idsForGame in self.idsForGames[matchIndex + 1:]:
            if player.getMemberId() not in idsForGame:
                return False
        return True
    
    def validate(self, team1: Team, team2: Team, matchNumber: int, putupPlayer: Player):
        self.validateAllPlayersAvailableForAtLeastOneMatch(team1, matchNumber)
        self.validateAllPlayersAvailableForAtLeastOneMatch(team2, matchNumber if putupPlayer is None else matchNumber + 1)
        self.validateAnyPlayersAvailableForMatch(team1, matchNumber)
        self.validateAnyPlayersAvailableForMatch(team2, matchNumber if putupPlayer is None else matchNumber + 1)
        self.validateMatchupCollisions(team1, matchNumber)
        self.validateMatchupCollisions(team2, matchNumber if putupPlayer is None else matchNumber + 1) 
    
    def validateAllPlayersAvailableForAtLeastOneMatch(self, team: Team, matchNumber: int):
        for player in team.getPlayers():
            isPlayerAvailable = False
            for idsForGame in self.idsForGames[matchNumber:]:
                if player.getMemberId() not in idsForGame:
                    isPlayerAvailable = True
                    break
            if not isPlayerAvailable:
                raise InvalidTeamMatchCriteria(f"ERROR: {player.getPlayerName()} from team {team.getTeamName()} is unavailable for the rest of the matches")

    def validateMatchupCollisions(self, team: Team, matchNumber: int):
        availableMatches = {}
        for player in team.getPlayers():
            availableMatchesForPlayer = []
            for idx, idsForGame in enumerate(self.idsForGames[matchNumber:]):
                if player.getMemberId() not in idsForGame:
                    availableMatchesForPlayer.append(idx + matchNumber)
            if tuple(availableMatchesForPlayer) in list(availableMatches.keys()):
                availableMatches[tuple(availableMatchesForPlayer)].append(player)
            else:
                availableMatches[tuple(availableMatchesForPlayer)] = [player]
        
        while True:
            restrictiveMatchSet = None
            for matchSet, players in availableMatches.items():
                if len(matchSet) < len(players):
                    raise InvalidTeamMatchCriteria(f"ERROR: {list(map(lambda player: player.getPlayerName(), players))} all need to play in matches {list(matchSet)}, which is not possible")

                if len(matchSet) == 0:
                    raise InvalidTeamMatchCriteria(f"ERROR: {list(map(lambda player: player.getPlayerName(), players))} can't play any matches")
                if len(matchSet) == len(players):
                    restrictiveMatchSet = matchSet
                    break
            if restrictiveMatchSet is not None:
                availableMatches = self.resetAvailableMatches(availableMatches, restrictiveMatchSet)
            else:
                break

    def resetAvailableMatches(self, originalAvailableMatches, restrictiveMatchSet):
        newAvailableMatches = {}
        originalAvailableMatches.pop(restrictiveMatchSet)
        for matchSet, players in originalAvailableMatches.items():
            for matchNumber in restrictiveMatchSet:
                if matchNumber in matchSet:
                    newMatchSet = list(matchSet)
                    newMatchSet.remove(matchNumber)
            newAvailableMatches[tuple(newMatchSet)] = players
        return newAvailableMatches

    def validateAnyPlayersAvailableForMatch(self, team: Team, matchNumber):
        for matchNumberInQuestion in range(matchNumber, NUM_PLAYERMATCHES_IN_TEAMMATCH):
            
            someoneAvailableForMatch = False
            for player in team.getPlayers():
                if player.getMemberId() not in self.idsForGames[matchNumberInQuestion]:
                    someoneAvailableForMatch = True
                    break
            if not someoneAvailableForMatch:
                raise InvalidTeamMatchCriteria(f"ERROR: no one available to play match {matchNumberInQuestion + 1}")