def nineBallSkillLevelMapper():
        map = {}
        map["14"] = "1"
        map["19"] = "2"
        map["25"] = "3"
        map["31"] = "4"
        map["38"] = "5"
        map["46"] = "6"
        map["55"] = "7"
        map["65"] = "8"
        map["75"] = "9"
        return map
    
def removeElements(testList, item): 
        res = list(filter((item).__ne__, testList)) 
        return res

def eightBallGamesNeededMapper():
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

