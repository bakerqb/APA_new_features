from termcolor import colored
from utils.Colors import Colors
def color_player(player_result, player_info):
    if player_result.get_did_win():
        return colored(str(player_info), Colors.GREEN)
    else:
        return colored(str(player_info), Colors.RED)

def color_plain_text(text):
    return colored(text)

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
    
    def get_map(self):
        return self.map