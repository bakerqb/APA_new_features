import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dataClasses.IScore import IScore


class NineBallScore(IScore):
    def __init__(self, matchPtsEarned: int, ballPtsEarned: int, ballPtsNeeded: int):
        self.matchPtsEarned = int(matchPtsEarned)
        self.ballPtsEarned = int(ballPtsEarned)
        self.ballPtsNeeded = int(ballPtsNeeded)

    def toJson(self):
        return {
            "matchPtsEarned": self.matchPtsEarned,
            "ballPtsEarned": self.ballPtsEarned,
            "ballPtsNeeded": self.ballPtsNeeded
        }
    
    def getMatchPtsEarned(self):
        return self.matchPtsEarned
    
    def getBallPtsEarned(self):
        return self.ballPtsEarned
    
    def getBallPtsNeeded(self):
        return self.ballPtsNeeded