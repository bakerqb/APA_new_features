class Session:
    def __init__(self, sessionId: int, sessionSeason: str, sessionYear: int):
        self.sessionId = sessionId
        self.sessionSeason = sessionSeason
        self.sessionYear = sessionYear

    def getSessionId(self):
        return self.sessionId
    
    def getSessionSeason(self):
        return self.sessionSeason
    
    def getSessionYear(self):
        return self.sessionYear
    
    def getPreviousSession(self):
        if self.sessionSeason == "SPRING":
            return Session(None, "FALL", self.sessionYear - 1)
        elif self.sessionSeason == "SUMMER":
            return Session(None, "SPRING", self.sessionYear)
        elif self.sessionSeason == "FALL":
            return Session(None, "SUMMER", self.sessionYear)
        
    def __eq__(self, session):
        return (
            self.sessionId == session.getSessionId() or 
            (self.sessionSeason == session.getSessionSeason() and self.sessionYear == session.getSessionYear())
        )