from src.srcMain.Database import Database
from src.converter.PlayerMatchConverter import PlayerMatchConverter
from src.converter.PlayerMatchWithASLConverter import PlayerMatchWithASLConverter
from utils.utils import *
from src.dataClasses.Format import Format
from tabulate import tabulate
from typing import List
from src.dataClasses.PlayerMatch import PlayerMatch
from statistics import median

db = Database()
playerMatchConverter = PlayerMatchConverter()
playerMatchWithASLConverter = PlayerMatchWithASLConverter()

def getAdjustedSkillLevel(memberId, currentSkillLevel, datePlayed):
        # NOTE: this calculation is only for the 8-ball format currently
        
        currentSkillLevel = int(currentSkillLevel)
        
        FORMAT = Format.EIGHT_BALL
        NUM_RELEVANT_PLAYERMATCHES = 15
        NUM_GAMES_CONSIDERED_RECENT = 5
        SKILL_LEVEL_CHANGE_ADJUSTMENT = .25
        MAX_ADJUSTED_SCORE_OFFSET = .49
        ADJUSTED_SCORE_OFFSET_THRESHOLD = .5

        playerResultsDb = db.getPlayerMatches(None, None, None, memberId, FORMAT, NUM_RELEVANT_PLAYERMATCHES, datePlayed, None, None, None)
        playerMatches = list(map(lambda playerMatch: playerMatchConverter.toPlayerMatchWithSql(playerMatch), playerResultsDb))

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
                        + (skillLevel1/getSkillLevelRangeForFormat(FORMAT)[-1]) 
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

        # Refine adjusted skill level if player has changed recently
        wasLowerSkillLevelRecently = False
        dateWhereWasLowerSkillLevel = None
        wasHigherSkillLevelRecently = False
        for playerMatch in playerMatches[:NUM_GAMES_CONSIDERED_RECENT]:
            playerResults = playerMatch.getPlayerResults()
            skillLevel = playerResults[0].getSkillLevel() if playerResults[0].getPlayer().getMemberId() == memberId else playerResults[1].getSkillLevel()
            if skillLevel < currentSkillLevel:
                wasLowerSkillLevelRecently = True
                dateWhereWasLowerSkillLevel = playerMatch.getDatePlayed()
                break
            elif skillLevel > currentSkillLevel:
                wasHigherSkillLevelRecently = True
                break
        
        wasCurrentSkillLevelBefore = False
        if wasLowerSkillLevelRecently:
            playerMatchesBeforeDateSql = db.getPlayerMatches(None, None, None, memberId, FORMAT, None, dateWhereWasLowerSkillLevel, None, None, None)
            playerMatchesBeforeDate = list(map(lambda playerMatch: playerMatchConverter.toPlayerMatchWithSql(playerMatch).properPlayerResultOrderWithPlayer(player), playerMatchesBeforeDateSql))
            for playerMatchBeforeDate in playerMatchesBeforeDate:
                if playerMatchBeforeDate.getPlayerResults()[0].getSkillLevel() >= currentSkillLevel:
                    wasCurrentSkillLevelBefore = True
                    break

        
        if wasLowerSkillLevelRecently and not wasCurrentSkillLevelBefore:
            adjustedScoreOffset -= SKILL_LEVEL_CHANGE_ADJUSTMENT
        if wasHigherSkillLevelRecently:
            adjustedScoreOffset += SKILL_LEVEL_CHANGE_ADJUSTMENT
        

        # If adjusted skill level is off the charts, set it to be max, like 4.99, for example
        if adjustedScoreOffset >= ADJUSTED_SCORE_OFFSET_THRESHOLD:
            adjustedScoreOffset = MAX_ADJUSTED_SCORE_OFFSET
        elif adjustedScoreOffset <= -1 * ADJUSTED_SCORE_OFFSET_THRESHOLD:
            adjustedScoreOffset = -1 * ADJUSTED_SCORE_OFFSET_THRESHOLD
        
        adjustedScoreOffset = float(f'{adjustedScoreOffset:.2f}')

        return round(int(currentSkillLevel) + ADJUSTED_SCORE_OFFSET_THRESHOLD + adjustedScoreOffset, 2)


def createASLMatrix(format: Format, expectedPtsMethod):
        db = Database()
        
        matrix = []
        matrix.append([])
        
        skillLevelRange = getSkillLevelRangeForFormat(format)
        matrix[0].append(0)
        for i in skillLevelRange:
            for section in SECTIONS_PER_SKILL_LEVEL:
                matrix[0].append(i + section[0])
        
        for skillLevel in skillLevelRange:
            for section in SECTIONS_PER_SKILL_LEVEL:
                matrix.append([skillLevel + section[0]] + ([1.5] * len(skillLevelRange) * len(SECTIONS_PER_SKILL_LEVEL)))
        for lowerSLIndex, lowerSL in enumerate(skillLevelRange):
            for higherSLIndex, higherSL in enumerate(skillLevelRange[lowerSLIndex:]):
                for lowerSectionIndex, lowerSection in enumerate(SECTIONS_PER_SKILL_LEVEL):
                    for higherSectionIndex, higherSection in enumerate(SECTIONS_PER_SKILL_LEVEL):
                        if lowerSL == higherSL and lowerSectionIndex > higherSectionIndex:
                            continue
                        
                        asl1range = [lowerSL + lowerSection[0], lowerSL + lowerSection[1]]
                        asl2range = [higherSL + higherSection[0], higherSL + higherSection[1]]
                        matchesLowAgainstHighSql = db.getPlayerMatches(None, None, None, None, format, None, None, None, asl1range, asl2range)
                        playerMatchesLowAgainstHigh = list(map(lambda playerMatchSql: playerMatchConverter.toPlayerMatchWithSql(playerMatchSql), matchesLowAgainstHighSql))
                        ptsEarnedByLowerPlayerRound1 = getPointsScoredByASLPlayers(0, playerMatchesLowAgainstHigh)
                        ptsEarnedByHigherPlayerRound1 = getPointsScoredByASLPlayers(1, playerMatchesLowAgainstHigh)


                        if lowerSL == higherSL and lowerSectionIndex == higherSectionIndex:
                            # Always use average when comparing players of the same adjusted skill level
                            numGames = len(playerMatchesLowAgainstHigh)
                            if numGames > 0:
                                sumPts = sum(ptsEarnedByLowerPlayerRound1 + ptsEarnedByHigherPlayerRound1) / 2
                                matrixIndex = (lowerSLIndex * len(SECTIONS_PER_SKILL_LEVEL)) + lowerSectionIndex + 1
                                matrix[matrixIndex][matrixIndex] = round(sumPts/numGames, 1)
                                
                            continue



                        asl1range = [higherSL + higherSection[0], higherSL + higherSection[1]]
                        asl2range = [lowerSL + lowerSection[0], lowerSL + lowerSection[1]]
                        matchesHighAgainstLowSql = db.getPlayerMatches(None, None, None, None, format, None, None, None, asl1range, asl2range)
                        playerMatchesHighAgainstLow = list(map(lambda playerMatchSql: playerMatchConverter.toPlayerMatchWithSql(playerMatchSql), matchesHighAgainstLowSql))
                        ptsEarnedByHigherPlayerRound2 = getPointsScoredByASLPlayers(0, playerMatchesHighAgainstLow)
                        ptsEarnedByLowerPlayerRound2 = getPointsScoredByASLPlayers(1, playerMatchesHighAgainstLow)


                        numGames = len(playerMatchesLowAgainstHigh) + len(playerMatchesHighAgainstLow)
                        if numGames > 0:
                            totalPtsEarnedByLowerPlayer = ptsEarnedByLowerPlayerRound1 + ptsEarnedByLowerPlayerRound2
                            totalPtsEarnedByHigherPlayer = ptsEarnedByHigherPlayerRound1 + ptsEarnedByHigherPlayerRound2
                            lowerIndexIndexyPoo = (lowerSLIndex * len(SECTIONS_PER_SKILL_LEVEL)) + lowerSectionIndex + 1
                            higherIndexIndexyPoo = ((higherSLIndex + lowerSLIndex) * len(SECTIONS_PER_SKILL_LEVEL)) + higherSectionIndex + 1
                            # TODO: Remove hardcoded check til issue 39 is resolved
                            if lowerSL == 4 and higherSL == 5 and lowerSectionIndex == 0 and higherSectionIndex == 2:
                                matrix[lowerIndexIndexyPoo][higherIndexIndexyPoo] = 1.2
                                matrix[higherIndexIndexyPoo][lowerIndexIndexyPoo] = 1.2
                            else:
                                if expectedPtsMethod == "average":
                                    matrix[lowerIndexIndexyPoo][higherIndexIndexyPoo] = roundNumber(totalPtsEarnedByLowerPlayer, numGames, True)
                                    matrix[higherIndexIndexyPoo][lowerIndexIndexyPoo] = roundNumber(totalPtsEarnedByHigherPlayer, numGames, True)
                                elif expectedPtsMethod == "median":
                                    matrix[lowerIndexIndexyPoo][higherIndexIndexyPoo] = roundNumber(totalPtsEarnedByLowerPlayer, numGames, False)
                                    matrix[higherIndexIndexyPoo][lowerIndexIndexyPoo] = roundNumber(totalPtsEarnedByHigherPlayer, numGames, False)
                                elif expectedPtsMethod.startswith("mix"):
                                    numGamesBaseline = int(expectedPtsMethod.replace("mix", ""))
                                    if numGames > numGamesBaseline:
                                        matrix[lowerIndexIndexyPoo][higherIndexIndexyPoo] = roundNumber(totalPtsEarnedByLowerPlayer, numGames, True)
                                        matrix[higherIndexIndexyPoo][lowerIndexIndexyPoo] = roundNumber(totalPtsEarnedByHigherPlayer, numGames, True)
                                    else:
                                        matrix[lowerIndexIndexyPoo][higherIndexIndexyPoo] = roundNumber(totalPtsEarnedByLowerPlayer, numGames, False)
                                        matrix[higherIndexIndexyPoo][lowerIndexIndexyPoo] = roundNumber(totalPtsEarnedByHigherPlayer, numGames, False)
                        
        print(tabulate(matrix, headers="firstrow", tablefmt="fancy_grid"))

        return matrix

def roundNumber(ptsList: List[int], numGames: int, isAverage: bool):
    finalNumber = 0
    if isAverage:
        finalNumber = round(sum(ptsList)/numGames, 1)
    else:
        finalNumber = round(median(ptsList), 1)
    if float(finalNumber).is_integer():
        finalNumber = int(finalNumber)
    return finalNumber



def getPointsScoredByASLPlayers(index, playerMatches: List[PlayerMatch]):
    return list(map(lambda playerMatch: playerMatch.getPlayerResults()[index].getScore().getTeamPtsEarned(), playerMatches))


############ Currently unused methods ############
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