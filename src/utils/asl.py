from src.srcMain.Database import Database
from src.converter.Converter import Converter
from utils.utils import *
from dataClasses.Format import Format

db = Database()
converter = Converter()

def getAdjustedSkillLevel(memberId, currentSkillLevel, datePlayed):
        # NOTE: this calculation is only for the 8-ball format currently
        currentSkillLevel = int(currentSkillLevel)
        
        FORMAT = Format.EIGHT_BALL
        NUM_RELEVANT_PLAYERMATCHES = 15
        NUM_GAMES_CONSIDERED_RECENT = 5
        SKILL_LEVEL_CHANGE_ADJUSTMENT = .25
        MAX_ADJUSTED_SCORE_OFFSET = .49
        ADJUSTED_SCORE_OFFSET_THRESHOLD = .49
        AVERAGE_OFFSET = .5

        playerResultsDb = db.getPlayerMatches(None, None, None, memberId, FORMAT, NUM_RELEVANT_PLAYERMATCHES, datePlayed, None, None, None)
        playerMatches = list(map(lambda playerMatch: converter.toPlayerMatchWithSql(playerMatch), playerResultsDb))

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
            playerMatchesBeforeDate = list(map(lambda playerMatch: converter.toPlayerMatchWithSql(playerMatch).properPlayerResultOrderWithPlayer(player), playerMatchesBeforeDateSql))
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

        return round(int(currentSkillLevel) + AVERAGE_OFFSET + adjustedScoreOffset, 2)


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