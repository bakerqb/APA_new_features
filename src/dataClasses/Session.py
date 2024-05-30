class Session:
    def __init__(self, sessionId: int, sessionSeason: str, sessionYear: int):
        self.sessionId = sessionId
        self.sessionSeason = sessionSeason
        self.sessionYear = sessionYear

    def toJson(self):
        return {
            "sessionId": self.sessionId,
            "sessionSeason": self.sessionSeason,
            "sessionYear": self.sessionYear
        }