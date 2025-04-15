from datetime import datetime
from dataClasses.Format import Format
from typeguard import typechecked
from typing import List, Dict, Tuple

EIGHT_BALL_SKILL_LEVEL_RANGE = range(2, 8)
NINE_BALL_SKILL_LEVEL_RANGE = range(1, 10)
DEFAULT_SKILL_LEVEL = 3
EIGHT_BALL_INCORRECT_SKILL_LEVEL = 1
NEW_PLAYER_SCRAPED_SKILL_LEVEL = 0
NUM_PLAYERMATCHES_IN_TEAMMATCH = 5
SKILL_LEVEL_CAP = 23
MASTERS_PTS_NEEDED = 7

NUM_SECTIONS_PER_SKILL_LEVEL = 3
SECTIONS_PER_SKILL_LEVEL = [(0, 0.42), (0.42, 0.58), (0.58, 1)]

@typechecked
def nineBallSkillLevelMapper() -> Dict[int, int]:
        map = {}
        map[14] = 1
        map[19] = 2
        map[25] = 3
        map[31] = 4
        map[38] = 5
        map[46] = 6
        map[55] = 7
        map[65] = 8
        map[75] = 9
        return map

@typechecked
def removeElements(words: List[str], removableWordList: List[str]) -> List[str]:
        for removableWord in removableWordList:
            words = list(filter((removableWord).__ne__, words)) 
        return words

@typechecked
def eightBallGamesNeededMapper() -> Dict[Tuple[int, int], Tuple[int, int]]:
    map = {}
    map[(2, 2)] = (2, 2)
    map[(2, 3)] = (2, 3)
    map[(2, 4)] = (2, 4)
    map[(2, 5)] = (2, 5)
    map[(2, 6)] = (2, 7)
    map[(3, 3)] = (2, 2)
    map[(3, 4)] = (2, 3)
    map[(3, 5)] = (2, 4)
    map[(3, 6)] = (2, 5)
    map[(3, 7)] = (2, 6)
    map[(4, 4)] = (3, 3)
    map[(4, 5)] = (3, 4)
    map[(4, 6)] = (3, 5)
    map[(4, 7)] = (2, 5)
    map[(5, 5)] = (4, 4)
    map[(5, 6)] = (4, 5)
    map[(6, 6)] = (5, 5)
    map[(6, 7)] = (4, 5)
    map[(7, 7)] = (5, 5)
    map[(3, 2)] = (3, 2)
    map[(4, 2)] = (4, 2)
    map[(5, 2)] = (5, 2)
    map[(6, 2)] = (6, 2)
    map[(4, 3)] = (3, 2)
    map[(5, 3)] = (4, 2)
    map[(6, 3)] = (5, 2)
    map[(7, 3)] = (6, 2)
    map[(5, 4)] = (4, 3)
    map[(6, 4)] = (5, 3)
    map[(7, 4)] = (5, 2)
    map[(6, 5)] = (5, 4)
    map[(7, 6)] = (5, 4)
    
    return map

@typechecked
def eightBallTeamPtsEarnedMapper(playerPtsEarned1: int, playerPtsEarned2: int, playerPtsNeeded1: int, playerPtsNeeded2: int) -> tuple:
    if playerPtsEarned1 == playerPtsNeeded1:
        if playerPtsEarned2 == 0:
            return (3, 0)
        elif playerPtsEarned2 == playerPtsNeeded2 - 1:
            return (2, 1)
        else:
            return (2, 0)
    else:
        if playerPtsEarned1 == 0:
            return (0, 3)
        elif playerPtsEarned1 == playerPtsNeeded1 - 1:
            return (1, 2)
        else:
            return (0, 2)
        
@typechecked
def eightBallNewPlayerMapper(oldPlayerSkillLevel: int, newPlayerTeamPtsEarned: int, oldPlayerTeamPtsEarned: int) -> tuple:
    if oldPlayerSkillLevel == 2:
        if newPlayerTeamPtsEarned == 3 and oldPlayerTeamPtsEarned == 0:
            return ((3, 3), (0, 2))
        elif newPlayerTeamPtsEarned == 2 and oldPlayerTeamPtsEarned == 1:
            return ((3, 3), (1, 2))
        elif newPlayerTeamPtsEarned == 1 and oldPlayerTeamPtsEarned == 2:
            return ((2, 3), (2, 2))
        elif newPlayerTeamPtsEarned == 0 and oldPlayerTeamPtsEarned == 2:
            return ((1, 3), (2, 2))
        else:
            return ((0, 3), (2, 2))
    elif oldPlayerSkillLevel == 3 or oldPlayerSkillLevel == NEW_PLAYER_SCRAPED_SKILL_LEVEL:
        if newPlayerTeamPtsEarned == 3 and oldPlayerTeamPtsEarned == 0:
            return ((2, 2), (0, 2))
        elif newPlayerTeamPtsEarned == 2 and oldPlayerTeamPtsEarned == 1:
            return ((2, 2), (1, 2))
        elif newPlayerTeamPtsEarned == 1 and oldPlayerTeamPtsEarned == 2:
            return ((1, 2), (2, 2))
        else:
            return ((0, 2), (2, 2))
    elif oldPlayerSkillLevel == 4:
        if newPlayerTeamPtsEarned == 3 and oldPlayerTeamPtsEarned == 0:
            return ((2, 2), (0, 3))
        elif newPlayerTeamPtsEarned == 2 and oldPlayerTeamPtsEarned == 0:
            return ((2, 2), (1, 3))
        elif newPlayerTeamPtsEarned == 2 and oldPlayerTeamPtsEarned == 1:
            return ((2, 2), (2, 3))
        elif newPlayerTeamPtsEarned == 1 and oldPlayerTeamPtsEarned == 2:
            return ((1, 2), (3, 3))
        else:
            return ((0, 2), (3, 3))
    elif oldPlayerSkillLevel == 5:
        if newPlayerTeamPtsEarned == 3 and oldPlayerTeamPtsEarned == 0:
            return ((2, 2), (0, 4))
        elif newPlayerTeamPtsEarned == 2 and oldPlayerTeamPtsEarned == 0:
            return ((2, 2), (1, 4))
        elif newPlayerTeamPtsEarned == 2 and oldPlayerTeamPtsEarned == 1:
            return ((2, 2), (3, 4))
        elif newPlayerTeamPtsEarned == 1 and oldPlayerTeamPtsEarned == 2:
            return ((1, 2), (4, 4))
        else:
            return ((0, 2), (4, 4))
    elif oldPlayerSkillLevel == 6:
        if newPlayerTeamPtsEarned == 3 and oldPlayerTeamPtsEarned == 0:
            return ((2, 2), (0, 5))
        elif newPlayerTeamPtsEarned == 2 and oldPlayerTeamPtsEarned == 0:
            return ((2, 2), (1, 5))
        elif newPlayerTeamPtsEarned == 2 and oldPlayerTeamPtsEarned == 1:
            return ((2, 2), (4, 5))
        elif newPlayerTeamPtsEarned == 1 and oldPlayerTeamPtsEarned == 2:
            return ((1, 2), (5, 5))
        else:
            return ((0, 2), (5, 5))
    else:
        if newPlayerTeamPtsEarned == 3 and oldPlayerTeamPtsEarned == 0:
            return ((2, 2), (0, 6))
        elif newPlayerTeamPtsEarned == 2 and oldPlayerTeamPtsEarned == 0:
            return ((2, 2), (1, 6))
        elif newPlayerTeamPtsEarned == 2 and oldPlayerTeamPtsEarned == 1:
            return ((2, 2), (5, 6))
        elif newPlayerTeamPtsEarned == 1 and oldPlayerTeamPtsEarned == 2:
            return ((1, 2), (6, 6))
        else:
            return ((0, 2), (6, 6))

@typechecked  
def toReadableDateTimeString(date: str) -> str:
    try:
        readableDate = datetime.strptime(date, "%Y-%m-%d").strftime("%B %-d, %Y")
        return readableDate
    except Exception:
        return date

@typechecked
def getSkillLevelRangeForFormat(format: Format) -> range:
    if format.value == Format.EIGHT_BALL.value:
        return EIGHT_BALL_SKILL_LEVEL_RANGE
    elif format.value == Format.NINE_BALL.value:
        return NINE_BALL_SKILL_LEVEL_RANGE