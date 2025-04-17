from dataClasses.Player import Player
from utils.utils import *
from typing import List, Set, Dict, Tuple
from dataClasses.Team import Team
from src.exceptions.InvalidTeamMatchCriteria import InvalidTeamMatchCriteria
from src.srcMain.Typechecked import Typechecked

class TeamMatchCriteria(Typechecked):
    def __init__(self, teamMatchCriteriaRawInput: List[str], team1: Team, team2: Team, matchNumber: int, putupPlayer: Player | None):
        # Formatted as a list of set of ids, where the first element signifies which players cannot play in game 1
        self.idsForGames = [set() for i in range(NUM_PLAYERMATCHES_IN_TEAMMATCH)]

        for criteria in teamMatchCriteriaRawInput:
            id, matchNumberTemp = criteria.split('-')
            self.idsForGames[int(matchNumberTemp)].add(int(id))
        
        self.validate(team1, team2, matchNumber, putupPlayer)
        
        for team in [team1, team2]:
            self.furtherCriteria(team)
        print("here")

    def furtherCriteria(self, team: Team) -> None:
        changesMade = True
        while changesMade:
            changesMade = False
            teamMemberIds = team.getMemberIds()
            # See if there is a match where only one person can play
            tempIdsForGames = self.idsForGames
            for matchNumber, ids in enumerate(self.idsForGames):
                teamMembersWhoCantPlayThisMatch = [id for id in teamMemberIds if id in ids]
                if len(teamMembersWhoCantPlayThisMatch) == NUM_PLAYERMATCHES_IN_TEAMMATCH - 1:
                    mustPlayMemberIdList = [id for id in teamMemberIds if id not in ids]
                    assert(len(mustPlayMemberIdList) == 1)
                    mustPlayMemberId = mustPlayMemberIdList[0]

                    matchNumbers = [i for i in range(NUM_PLAYERMATCHES_IN_TEAMMATCH)]
                    matchNumbers.remove(matchNumber)
                    
                    for i in matchNumbers:
                        if mustPlayMemberId not in tempIdsForGames[i]:
                            tempIdsForGames[i].add(mustPlayMemberId)
                            changesMade = True
                    
            
            self.idsForGames = tempIdsForGames


            # See if there is a player who can only play in one match
            for memberId in teamMemberIds:
                matchesTheyCanPlay = []
                for matchNumber, ids in enumerate(self.idsForGames):
                    if memberId not in self.idsForGames[matchNumber]:
                        matchesTheyCanPlay.append(matchNumber)
                    if len(matchesTheyCanPlay) > 1:
                        break
                
                assert(len(matchesTheyCanPlay) > 0)
                if len(matchesTheyCanPlay) == 1:
                    allOtherTeamMembers = teamMemberIds.copy()
                    allOtherTeamMembers.remove(memberId)
                    if not set(allOtherTeamMembers).issubset(tempIdsForGames[matchesTheyCanPlay[0]]):
                        tempIdsForGames[matchesTheyCanPlay[0]].update(allOtherTeamMembers)
                        changesMade = True
            self.idsForGames = tempIdsForGames

    def getMemberIdsForGame(self, gameIndex: int) -> Set[int]:
        return self.idsForGames[gameIndex]
    
    def playerMustPlay(self, player: Player, matchIndex: int, numUniquePlayersFromStart: int) -> bool:
        if numUniquePlayersFromStart > NUM_PLAYERMATCHES_IN_TEAMMATCH:
            return False
        
        for idsForGame in self.idsForGames[matchIndex + 1:]:
            if player.getMemberId() not in idsForGame:
                return False
        return True
    
    def validate(self, team1: Team, team2: Team, matchNumber: int, putupPlayer: Player | None) -> None:
        self.validateAllPlayersAvailableForAtLeastOneMatch(team1, matchNumber)
        self.validateAllPlayersAvailableForAtLeastOneMatch(team2, matchNumber if putupPlayer is None else matchNumber + 1)
        self.validateAnyPlayersAvailableForMatch(team1, matchNumber)
        self.validateAnyPlayersAvailableForMatch(team2, matchNumber if putupPlayer is None else matchNumber + 1)
        self.validateMatchupCollisions(team1, matchNumber)
        self.validateMatchupCollisions(team2, matchNumber if putupPlayer is None else matchNumber + 1) 
    
    def validateAllPlayersAvailableForAtLeastOneMatch(self, team: Team, matchNumber: int) -> None:
        for player in team.getPlayers():
            isPlayerAvailable = False
            for idsForGame in self.idsForGames[matchNumber:]:
                if player.getMemberId() not in idsForGame:
                    isPlayerAvailable = True
                    break
            if not isPlayerAvailable:
                raise InvalidTeamMatchCriteria(f"ERROR: {player.getPlayerName()} from team {team.getTeamName()} is unavailable for the rest of the matches")

    def validateMatchupCollisions(self, team: Team, matchNumber: int) -> None:
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
        
        for matchSet, players in availableMatches.items():
                if len(matchSet) == 0:
                    raise InvalidTeamMatchCriteria(f"ERROR: {list(map(lambda player: player.getPlayerName(), players))} can't play any matches")

    def resetAvailableMatches(self, originalAvailableMatches: Dict, restrictiveMatchSet: Tuple) -> Dict:
        newAvailableMatches = {}
        originalAvailableMatches.pop(restrictiveMatchSet)
        for matchSet, players in originalAvailableMatches.items():
            newMatchSet = None
            for matchNumber in restrictiveMatchSet:
                if matchNumber in matchSet:
                    newMatchSet = list(matchSet)
                    newMatchSet.remove(matchNumber)
            if newMatchSet is not None:
                newAvailableMatches[tuple(newMatchSet)] = players
        return newAvailableMatches

    def validateAnyPlayersAvailableForMatch(self, team: Team, matchNumber: int) -> None:
        for matchNumberInQuestion in range(matchNumber, NUM_PLAYERMATCHES_IN_TEAMMATCH):
            
            someoneAvailableForMatch = False
            for player in team.getPlayers():
                if player.getMemberId() not in self.idsForGames[matchNumberInQuestion]:
                    someoneAvailableForMatch = True
                    break
            if not someoneAvailableForMatch:
                raise InvalidTeamMatchCriteria(f"ERROR: no one from {team.getTeamName()} available to play match {matchNumberInQuestion + 1}")