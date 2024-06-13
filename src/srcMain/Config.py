import yaml
import os

class Config:
    def __init__(self):
        with open(self.findConfigFile(), 'r') as config_file:
            self.config = yaml.safe_load(config_file)
    
    def getConfig(self):
        return self.config

    def findConfigFile(self):
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        name = 'application.yml'
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

    def getSessionConfig(self, isEightBall):
        return self.config.get('eightBallData') if isEightBall else self.config.get('nineBallData')