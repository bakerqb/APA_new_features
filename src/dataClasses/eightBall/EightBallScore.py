import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dataClasses.IScore import IScore


class EightBallScore(IScore):
    def __init__(self, matchPtsEarned: int, gamesWon: int, gamesNeeded: int):
        self.matchPtsEarned = int(matchPtsEarned)
        self.gamesWon = int(gamesWon)
        self.gamesNeeded = int(gamesNeeded)

    def toJson(self):
        return {
            "matchPtsEarned": self.matchPtsEarned,
            "gamesWon": self.gamesWon,
            "gamesNeeded":self.gamesNeeded
        }
    