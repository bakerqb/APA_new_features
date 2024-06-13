import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.utils import *
from dataClasses.IPlayerMatch import IPlayerMatch
from dataClasses.Team import Team

class EightBallPlayerMatch(IPlayerMatch):
    def __init__(self):
        pass
    
    def initWithDiv(self, matchDiv, team1: Team, team2: Team, playerMatchId: int, teamMatchId: int, datePlayed):
        textElements = matchDiv.text.split('\n')
        textElements = removeElements(textElements, 'LAG')
        textElements = removeElements(textElements, 'SL')
        textElements = removeElements(textElements, 'Pts Earned')
        textElements = removeElements(textElements, 'GW/GMW')
        
        playerName1 = textElements[0]
        skillLevel1 = textElements[1]
        matchPtsEarned1 = textElements[2]

        score = textElements[4]
        scoreElements = score.split(' - ')
        score1 = scoreElements[0].split('/')
        if len(score1) == 1:
            score1.insert(0, 0)
        score2 = scoreElements[1].split('/')
        if len(score2) == 1:
            score2.insert(0, 0)

        gamesWon1, gamesNeeded1 = score1
        
        gamesWon2, gamesNeeded2 = score2
        skillLevel2 = textElements[5]
        playerName2 = textElements[6]
        matchPtsEarned2 = textElements[7]

        return self.initWithDirectInfo(playerMatchId, teamMatchId, playerName1, team1, skillLevel1, matchPtsEarned1, gamesWon1, gamesNeeded1,
                   playerName2, team2, skillLevel2, matchPtsEarned2, gamesWon2, gamesNeeded2, datePlayed, True)