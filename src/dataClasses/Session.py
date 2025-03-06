from dataClasses.SessionSeason import SessionSeason

class Session:
    def __init__(self, sessionId: int, sessionSeason: SessionSeason, sessionYear: int):
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
        if self.sessionSeason == SessionSeason.SPRING:
            return Session(None, SessionSeason.FALL, self.sessionYear - 1)
        elif self.sessionSeason == SessionSeason.SUMMER:
            return Session(None, SessionSeason.SPRING, self.sessionYear)
        elif self.sessionSeason == SessionSeason.FALL:
            return Session(None, SessionSeason.SUMMER, self.sessionYear)
        
    def __eq__(self, session):
        return (
            self.sessionId == session.getSessionId() or 
            (self.sessionSeason == session.getSessionSeason() and self.sessionYear == session.getSessionYear())
        )