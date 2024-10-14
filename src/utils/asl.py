from src.srcMain.Database import Database
from src.converter.Converter import Converter
from utils.utils import *
from src.dataClasses.Game import Game
from tabulate import tabulate


def getAdjustedSkillLevel(memberId, currentSkillLevel, datePlayed, playerMatchId):
        currentSkillLevel = int(currentSkillLevel)
        db = Database()
        converter = Converter()

        # TODO: remove hardcoded values
        limit = 15
        game = Game.EightBall.value

        playerResultsDb = db.getPlayerMatches(None, None, memberId, game, limit, datePlayed, playerMatchId)
        playerMatches = list(map(lambda playerMatch: converter.toPlayerMatchWithSql(playerMatch), playerResultsDb))

        #TODO: put playerMatches through algorithm
        adjustedScoreOffsetTotal = 0
        numWins = 0
        numLosses = 0
        for playerMatch in playerMatches:
            playerResults = playerMatch.getPlayerResults()
            player = playerResults[0].getPlayer() if playerResults[0].getPlayer().getMemberId() == memberId else playerResults[1].getPlayer()

            playerMatch = playerMatch.properPlayerResultOrderWithPlayer(player)
            
            # Make sure you know who the opponent and who the "YOU" player is
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

            didWin = int(gamesWon0/gamesNeeded0)
            if didWin:
                numWins += 1
            else:
                numLosses += 1

            adjustedScoreOffset = (
                    (
                        ((gamesNeeded1 - gamesWon1)-(gamesNeeded0 - gamesWon0))/(gamesNeeded1 + gamesNeeded0)
                    )
                    *
                    abs(
                        didWin
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
            if adjustedScoreOffset > 0:
                adjustedScoreOffset *= (numWins/10)
            elif adjustedScoreOffset < 0:
                adjustedScoreOffset *= (numLosses/10)

        if memberId == 60902883:
            adjustedScoreOffset -= 1
        if adjustedScoreOffset >= .5:
            adjustedScoreOffset = .49
        elif adjustedScoreOffset <= -.5:
            adjustedScoreOffset = -.49
        
        adjustedScoreOffset = float(f'{adjustedScoreOffset:.2f}')

        return str(int(currentSkillLevel) + .5 + adjustedScoreOffset)


def createASLMatrix(game):
        db = Database()
        
        matrix = []
        matrix.append([])
        
        numSectionsPerSkillLevel = 3
        sectionsPerSkillLevel = [(0, 0.42), (0.42, 0.58), (0.58, 1)]
        numSkillLevels = 0
        if game == Game.EightBall.value:
            numSkillLevels = EIGHT_BALL_NUM_SKILL_LEVELS
        elif game == Game.NineBall.value:
            numSkillLevels = NINE_BALL_NUM_SKILL_LEVELS
        
        rangeStart = 0
        if game == Game.EightBall.value:
            rangeStart = 2
        elif game == Game.NineBall.value:
            rangeStart = 1
        matrix[0].append(0)
        for i in range(rangeStart, numSkillLevels + 1):
            for section in sectionsPerSkillLevel:
                matrix[0].append(i + section[0])
        
        for skillLevel in range(rangeStart, numSkillLevels + 1):
            for section in sectionsPerSkillLevel:
                matrix.append([skillLevel + section[0]] + ([1.5] * (numSkillLevels - rangeStart + 1) * numSectionsPerSkillLevel))
        for lowerSLIndex, lowerSL in enumerate(range(rangeStart, numSkillLevels + 1)):
            for higherSLIndex, higherSL in enumerate(range(lowerSL, numSkillLevels + 1)):
                for lowerSectionIndex, lowerSection in enumerate(sectionsPerSkillLevel):
                    for higherSectionIndex, higherSection in enumerate(sectionsPerSkillLevel):
                        if lowerSL == higherSL and lowerSectionIndex > higherSectionIndex:
                            continue
                        
                        matchesLowAgainstHigh = db.cur.execute(
                            "SELECT SUM(s1.teamPtsEarned), SUM(s2.teamPtsEarned), COUNT(*) " + 
                            "FROM Division d " +
                            "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                            "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                            "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                            f"WHERE pm.adjustedSkillLevel1 >= {lowerSL + lowerSection[0]} " +
                            f"AND pm.adjustedSkillLevel1 < {lowerSL + lowerSection[1]} " +
                            f"AND pm.adjustedSkillLevel2 >= {higherSL + higherSection[0]} " +
                            f"AND pm.adjustedSkillLevel2 < {higherSL + higherSection[1]} " +
                            f"AND d.game = '{game}'"
                        ).fetchone()

                        if lowerSL == higherSL and lowerSectionIndex == higherSectionIndex:
                            games = matchesLowAgainstHigh[2]
                            if games > 0:
                                pts = ((matchesLowAgainstHigh[0] if matchesLowAgainstHigh[0] else 0)  + (matchesLowAgainstHigh[1] if matchesLowAgainstHigh[1] else 0)) / 2
                                matrixIndex = (lowerSLIndex * numSectionsPerSkillLevel) + lowerSectionIndex + 1
                                matrix[matrixIndex][matrixIndex] = round(pts/games, 1)
                                
                            continue

                        matchesHighAgainstLow = db.cur.execute(
                            "SELECT SUM(s1.teamPtsEarned), SUM(s2.teamPtsEarned), COUNT(*) " + 
                            "FROM Division d " +
                            "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                            "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                            "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                            f"WHERE pm.adjustedSkillLevel1 >= {higherSL + higherSection[0]} " +
                            f"AND pm.adjustedSkillLevel1 < {higherSL + higherSection[1]} " +
                            f"AND pm.adjustedSkillLevel2 >= {lowerSL + lowerSection[0]} " +
                            f"AND pm.adjustedSkillLevel2 < {lowerSL + lowerSection[1]} " +
                            f"AND d.game = '{game}'"
                        ).fetchone()

                        games = matchesLowAgainstHigh[2] + matchesHighAgainstLow[2]
                        if games > 0:
                            ptsFromLowerRatedPlayer = (matchesLowAgainstHigh[0] if matchesLowAgainstHigh[0] else 0)  + (matchesHighAgainstLow[1] if matchesHighAgainstLow[1] else 0)
                            ptsFromHigherRatedPlayer = (matchesLowAgainstHigh[1] if matchesLowAgainstHigh[1] else 0) + (matchesHighAgainstLow[0] if matchesHighAgainstLow[0] else 0)
                            lowerIndexIndexyPoo = (lowerSLIndex * numSectionsPerSkillLevel) + lowerSectionIndex + 1
                            higherIndexIndexyPoo = ((higherSLIndex + lowerSLIndex) * numSectionsPerSkillLevel) + higherSectionIndex + 1
                            matrix[lowerIndexIndexyPoo][higherIndexIndexyPoo] = round(ptsFromLowerRatedPlayer/games, 1)
                            matrix[higherIndexIndexyPoo][lowerIndexIndexyPoo] = round(ptsFromHigherRatedPlayer/games, 1)
        
        
        print(tabulate(matrix, headers="firstrow", tablefmt="fancy_grid"))
        getPointSpread(game)
        return matrix

def getPointSpread(game):
    db = Database()

    totalMatches = db.cur.execute(
                            "SELECT COUNT(*) " + 
                            "FROM Division d " +
                            "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                            "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                            "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                            f"WHERE d.game = '{game}'"
                        ).fetchone()[0]

    matchesHighAgainstLow = db.cur.execute(
                            "SELECT COUNT(*) " + 
                            "FROM Division d " +
                            "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                            "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                            "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                            f"WHERE s1.teamPtsEarned = 0 " +
                            f"AND s2.teamPtsEarned = 3 " +
                            f"AND d.game = '{game}'"
                        ).fetchone()
    
    matchesLowAgainstHigh = db.cur.execute(
                            "SELECT COUNT(*) " + 
                            "FROM Division d " +
                            "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                            "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                            "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                            f"WHERE s1.teamPtsEarned = 3 " +
                            f"AND s2.teamPtsEarned = 0 " +
                            f"AND d.game = '{game}'"
                        ).fetchone()
    
    print("3-0's: " + str(matchesHighAgainstLow[0] + matchesLowAgainstHigh[0]) + " " + str(float((matchesHighAgainstLow[0] + matchesLowAgainstHigh[0])/totalMatches*100)) + "%")

    matchesHighAgainstLow = db.cur.execute(
                            "SELECT COUNT(*) " + 
                            "FROM Division d " +
                            "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                            "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                            "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                            f"WHERE s1.teamPtsEarned = 0 " +
                            f"AND s2.teamPtsEarned = 2 " +
                            f"AND d.game = '{game}'"
                        ).fetchone()
    
    matchesLowAgainstHigh = db.cur.execute(
                            "SELECT COUNT(*) " + 
                            "FROM Division d " +
                            "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                            "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                            "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                            f"WHERE s1.teamPtsEarned = 2 " +
                            f"AND s2.teamPtsEarned = 0 " +
                            f"AND d.game = '{game}'"
                        ).fetchone()
    
    print("2-0's: " + str(matchesHighAgainstLow[0] + matchesLowAgainstHigh[0]) + " " + str(float((matchesHighAgainstLow[0] + matchesLowAgainstHigh[0])/totalMatches*100)) + "%")

    matchesHighAgainstLow = db.cur.execute(
                            "SELECT COUNT(*) " + 
                            "FROM Division d " +
                            "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                            "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                            "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                            f"WHERE s1.teamPtsEarned = 1 " +
                            f"AND s2.teamPtsEarned = 2 " +
                            f"AND d.game = '{game}'"
                        ).fetchone()
    
    matchesLowAgainstHigh = db.cur.execute(
                            "SELECT COUNT(*) " + 
                            "FROM Division d " +
                            "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                            "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                            "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                            f"WHERE s1.teamPtsEarned = 2 " +
                            f"AND s2.teamPtsEarned = 1 " +
                            f"AND d.game = '{game}'"
                        ).fetchone()
    
    print("2-1's: " + str(matchesHighAgainstLow[0] + matchesLowAgainstHigh[0]) + " " + str(float((matchesHighAgainstLow[0] + matchesLowAgainstHigh[0])/totalMatches*100)) + "%")
