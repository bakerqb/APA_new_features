from dataClasses.Format import Format
from dataClasses.Session import Session
from src.srcMain.Typechecked import Typechecked

class Division(Typechecked):
    def __init__(self, session: Session, divisionId: int, divisionName: str, dayOfWeek: int, format):
        self.session = session
        self.divisionId = divisionId
        self.divisionName = divisionName
        self.dayOfWeek = dayOfWeek
        self.format = format
    
    def getSession(self) -> Session:
        return self.session
    
    def getDivisionId(self) -> int:
        return self.divisionId
    
    def getDivisionName(self) -> str:
        return self.divisionName
    
    def getDayOfWeek(self) -> int:
        return self.dayOfWeek
    
    def getFormat(self) -> Format:
        return self.format