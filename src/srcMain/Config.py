import yaml
import os
from typing import Dict

class Config:
    def __init__(self):
        with open(self.findConfigFile(), 'r') as config_file:
            self.config = yaml.safe_load(config_file)
    
    def getConfig(self) -> Dict:
        return self.config

    def findConfigFile(self)-> str:
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        name = 'application.yml'
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)