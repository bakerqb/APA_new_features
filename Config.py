import yaml

class Config:
    def __init__(self):
        with open('application.yml', 'r') as config_file:
            self.config = yaml.safe_load(config_file)
    
    def get_config(self):
        return self.config

        