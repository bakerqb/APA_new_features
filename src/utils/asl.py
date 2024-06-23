from src.srcMain.Database import Database
from src.converter.Converter import Converter
import math
import time
from utils.utils import *
from src.dataClasses.Game import Game


def getAdjustedSkillLevel(memberId, currentSkillLevel):
        
        db = Database()
        converter = Converter()

        # TODO: remove hardcoded values
        limit = 10
        game = Game.EightBall.value

        playerResultsDb = db.getLatestPlayerMatchesForPlayer(memberId, game, limit)
        start = time.time()
        playerMatches = list(map(lambda playerMatch: converter.toPlayerMatchWithSql(playerMatch), playerResultsDb))
        end = time.time()
        length = end - start
        print(f"conversion duration: {length} seconds")

        #TODO: put playerMatches through algorithm
        adjustedScoreOffsetTotal = 0
        for playerMatch in playerMatches:
            playerResults = playerMatch.getPlayerResults()
            player = playerResults[0].getPlayer() if playerResults[0].getPlayer().getMemberId() == memberId else playerResults[1].getPlayer()

            playerMatch = playerMatch.properPlayerResultOrderWithPlayer(player)
            
            # Make sure you know how the opponent and who the "YOU" player is
            # Then just plug that shit into the algorithm
            playerResult0 = playerMatch.getPlayerResults()[0]
            playerResult1 = playerMatch.getPlayerResults()[1]

            gamesWon1 = playerResult1.getScore().getPlayerPtsEarned()
            gamesWon0 = playerResult0.getScore().getPlayerPtsEarned()
            skillLevel0 = playerResult0.getSkillLevel()
            skillLevel1 = playerResult1.getSkillLevel()
            gamesNeeded0 = playerResult0.getScore().getPlayerPtsNeeded()
            gamesNeeded1 = playerResult1.getScore().getPlayerPtsNeeded()
            if gamesNeeded0 == 0 or gamesNeeded1 == 0:
                continue

            adjustedScoreOffset = (
                    (
                        ((gamesNeeded1 - gamesWon1)-(gamesNeeded0 - gamesWon0))/(gamesNeeded1 + gamesNeeded0)
                    )
                    *
                    abs(
                        math.ceil(gamesWon0/gamesNeeded0)
                        + (skillLevel1/EIGHT_BALL_NUM_SKILL_LEVELS) 
                        - 1
                    )
            )*3
            
            # If skill level is now lower
            if skillLevel0 > currentSkillLevel:
                weightHigher = 1 + (1 - (1/(skillLevel0 - currentSkillLevel + 1)))
                weightLower = 1 + (1/(currentSkillLevel - skillLevel0 -1))

                # And you won when higher
                if gamesWon0 == gamesNeeded0:
                    adjustedScoreOffset *= weightHigher
                # And you lost when higher
                else:
                    adjustedScoreOffset *= weightLower

            # If skill level is now higher
            elif skillLevel0 < currentSkillLevel:
                weightHigher = 1 + (1 - (1/(currentSkillLevel - skillLevel0 + 1)))
                weightLower = 1 + (1/(skillLevel0 - currentSkillLevel -1))

                # And you won when lower
                if gamesWon0 == gamesNeeded0:
                    adjustedScoreOffset *= weightLower
                # And you lost when lower
                else:
                    adjustedScoreOffset *= weightHigher

            adjustedScoreOffsetTotal += adjustedScoreOffset

        adjustedScoreOffset = 0
        if len(playerMatches) > 0:
            adjustedScoreOffset = adjustedScoreOffsetTotal/len(playerMatches)
        if adjustedScoreOffset >= .5:
            adjustedScoreOffset = .49
        elif adjustedScoreOffset <= -.5:
            adjustedScoreOffset = -.49
        
        end = time.time()
        length = end - start
        print(f"ASL calculation duration: {length} seconds")

        return str(currentSkillLevel + .5 + adjustedScoreOffset)
