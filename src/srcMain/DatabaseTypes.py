from typing import Tuple, List
from enum import Enum


class DatabaseTypes(Enum):
    PlayerMatch = Tuple[int, str, int, int, str, int, str,
                    int, str, int, int, int, str,
                    int, str, int, int, float, int, int, int,
                    int, int, str, int, str, int, int, float,
                    int, int, int]

    Player = Tuple[int, str, int]

    Division = Tuple[int, str, int, int, str, int, str]
    Session = Tuple[int, str, int]
    TeamMatch = Tuple[int, int]
    TeamWithoutRoster = Tuple[int, int, int, str]
    TeamWithRoster = List[Tuple[int, str, int, int, str, int, str, int, int, str, int, str, int]]
    PlayerWithDateLastPlayed = Tuple[int, str, int, str]