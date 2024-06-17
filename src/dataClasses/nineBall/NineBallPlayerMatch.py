import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.utils import *
from dataClasses.IPlayerMatch import IPlayerMatch
from dataClasses.Team import Team

class NineBallPlayerMatch(IPlayerMatch):
    def __init__(self):
        pass

    def initWithDiv(self, matchDiv, team1: Team, team2: Team, playerMatchId: int, teamMatchId: int, datePlayed):
        mapper = nineBallSkillLevelMapper()
        
        textElements = matchDiv.text.split('\n')
        textElements = removeElements(textElements, 'LAG')
        textElements = removeElements(textElements, 'SL')
        textElements = removeElements(textElements, 'Pts Earned')
        textElements = removeElements(textElements, 'PE/PN')
        
        playerName1 = textElements[0]
        matchPtsEarned1 = textElements[2]

        score = textElements[4]
        scoreElements = score.split(' - ')
        score1 = scoreElements[0].split('/')
        if len(score1) == 1:
            score1.insert(0, 0)
        score2 = scoreElements[1].split('/')
        if len(score2) == 1:
            score2.insert(0, 0)

        ballPtsEarned1, ballPtsNeeded1 = score1
        skillLevel1 = mapper.get(ballPtsNeeded1)
        ballPtsEarned2, ballPtsNeeded2 = score2

        skillLevel2 = mapper.get(ballPtsNeeded2)
        playerName2 = textElements[6]
        matchPtsEarned2 = textElements[7]

        return self.initWithDirectInfo(playerMatchId, teamMatchId, playerName1, team1, skillLevel1, matchPtsEarned1, ballPtsEarned1, ballPtsNeeded1,
                   playerName2, team2, skillLevel2, matchPtsEarned2, ballPtsEarned2, ballPtsNeeded2, datePlayed, False)
    
    