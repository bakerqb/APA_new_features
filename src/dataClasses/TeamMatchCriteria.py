from src.dataClasses.Player import Player
from utils.utils import *

class TeamMatchCriteria:
    def __init__(self, teamMatchCriteriaRawInput):
        # Formatted as a list of list of ids, where the first element signifies which players cannot play in game 1
        self.idsForGames = []
        for i in range(NUM_PLAYERMATCHES_IN_TEAMMATCH):
            self.idsForGames.append(set())
        for criteria in teamMatchCriteriaRawInput:
            id, matchNumber = criteria.split('-')
            self.idsForGames[int(matchNumber)].add(int(id))

    def getMemberIdsForGame(self, gameIndex):
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

