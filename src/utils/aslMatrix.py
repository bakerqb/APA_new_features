from src.srcMain.Database import Database
from src.converter.PlayerMatchWithASLConverter import PlayerMatchWithASLConverter
from utils.utils import *
from dataClasses.Format import Format
from tabulate import tabulate
from typing import List, Dict
from dataClasses.PlayerMatch import PlayerMatch
from statistics import median
import os
import json
from typeguard import typechecked

db = Database()
playerMatchWithASLConverter = PlayerMatchWithASLConverter()

@typechecked
def createASLMatrix(format: Format, expectedPtsMethod: str) -> List[List[float | int]]:
        db = Database()

        playerMatchesSql = db.getPlayerMatches(None, None, None, None, format, None, None, None, None, None)

        numPlayerMatches = len(playerMatchesSql)
        aslMatrixFilePath = os.path.abspath(__file__ + f"/../../resources/aslMatrix-{format.value}-{expectedPtsMethod}.json")
        existingASLMatrixData = parseExistingASLMatrix(aslMatrixFilePath)
        if numPlayerMatches <= existingASLMatrixData.get("numPlayerMatches") and expectedPtsMethod == existingASLMatrixData.get("expectedPtsMethod"):
            return existingASLMatrixData.get("aslMatrix")

        playerMatches = list(map(lambda playerMatchSql: playerMatchWithASLConverter.toPlayerMatchWithSql(playerMatchSql), playerMatchesSql))
        
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
                        playerMatchesLowAgainstHigh = list(filter(lambda playerMatch: asl1range[0] <= playerMatch.getPlayerResults()[0].getAdjustedSkillLevel() < asl1range[1] and asl2range[0] <= playerMatch.getPlayerResults()[1].getAdjustedSkillLevel() < asl2range[1], playerMatches))
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
                        playerMatchesHighAgainstLow = list(filter(lambda playerMatch: asl1range[0] <= playerMatch.getPlayerResults()[0].getAdjustedSkillLevel() < asl1range[1] and asl2range[0] <= playerMatch.getPlayerResults()[1].getAdjustedSkillLevel() < asl2range[1], playerMatches))
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


        data = {
            "aslMatrix": matrix,
            "numPlayerMatches": numPlayerMatches,
            "expectedPtsMethod": expectedPtsMethod
        }
        file = open(aslMatrixFilePath, "w")
        json.dump(data, file)
        file.close()

        return matrix

@typechecked
def roundNumber(ptsList: List[int], numGames: int, isAverage: bool) -> float | int:
    finalNumber = 0
    if isAverage:
        finalNumber = round(sum(ptsList)/numGames, 1)
    else:
        finalNumber = round(median(ptsList), 1)
    if float(finalNumber).is_integer():
        finalNumber = int(finalNumber)
    return finalNumber

@typechecked
def getPointsScoredByASLPlayers(index, playerMatches: List[PlayerMatch]) -> List[int]:
    return list(map(lambda playerMatch: playerMatch.getPlayerResults()[index].getScore().getTeamPtsEarned(), playerMatches))

@typechecked
def parseExistingASLMatrix(aslMatrixFilePath: str) -> Dict:
    if os.path.exists(aslMatrixFilePath):
        file = open(aslMatrixFilePath, "r")
        contents = json.load(file)
        file.close()
        return contents
    else:
        data = {
            "aslMatrix": [],
            "numPlayerMatches": 0,
            "expectedPtsMethod": "average"
        }
        return data
        

