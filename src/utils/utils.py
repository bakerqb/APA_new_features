class NineBallSkillLevelMapper:
    def __init__(self):
        self.map = {}
        self.map["14"] = "1"
        self.map["19"] = "2"
        self.map["25"] = "3"
        self.map["31"] = "4"
        self.map["38"] = "5"
        self.map["46"] = "6"
        self.map["55"] = "7"
        self.map["65"] = "8"
        self.map["75"] = "9"
    
    def getMap(self):
        return self.map
    
def removeElements(testList, item): 
        res = list(filter((item).__ne__, testList)) 
        return res