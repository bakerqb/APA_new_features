from dataClasses.SessionSeason import SessionSeason
from src.srcMain.Typechecked import Typechecked

class Session(Typechecked):
    def __init__(self, sessionId: int, sessionSeason: SessionSeason, sessionYear: int):
        self.sessionId = sessionId
        self.sessionSeason = sessionSeason
        self.sessionYear = sessionYear

    def getSessionId(self) -> int:
        return self.sessionId
    
    def getSessionSeason(self) -> SessionSeason:
        return self.sessionSeason
    
    def getSessionYear(self) -> int:
        return self.sessionYear
    
    def getPreviousSession(self):
        if self.sessionSeason == SessionSeason.SPRING:
            return Session(-1, SessionSeason.FALL, self.sessionYear - 1)
        elif self.sessionSeason == SessionSeason.SUMMER:
            return Session(-1, SessionSeason.SPRING, self.sessionYear)
        elif self.sessionSeason == SessionSeason.FALL:
            return Session(-1, SessionSeason.SUMMER, self.sessionYear)
        
    def __eq__(self, session) -> bool:
        return (
            self.sessionId == session.getSessionId() or 
            (self.sessionSeason == session.getSessionSeason() and self.sessionYear == session.getSessionYear())
        )