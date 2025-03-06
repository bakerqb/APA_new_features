from src.dataClasses.Format import Format
from dataClasses.Session import Session

class Division:
    def __init__(self, session: Session, divisionId: int, divisionName: str, dayOfWeek: int, format: Format):
        self.session = session
        self.divisionId = divisionId
        self.divisionName = divisionName
        self.dayOfWeek = dayOfWeek
        self.format = format
    
    def getSession(self):
        return self.session
    
    def getDivisionId(self):
        return self.divisionId
    
    def getDivisionName(self):
        return self.divisionName
    
    def getDayOfWeek(self):
        return self.dayOfWeek
    
    def getFormat(self):
        return self.format