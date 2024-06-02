from dataClasses.Game import Game
from dataClasses.Session import Session

class Division:
    def __init__(self, session: Session, divisionId: int, divisionName: str, dayOfWeek: int, game: Game):
        self.session = session
        self.divisionId = divisionId
        self.divisionName = divisionName
        self.dayOfWeek = dayOfWeek
        self.game = game

    def toJson(self):
        return {
            "session": self.session.toJson(),
            "divisionId": self.divisionId,
            "divisionName": self.divisionName,
            "dayOfWeek": self.dayOfWeek,
            "game": self.game
        }