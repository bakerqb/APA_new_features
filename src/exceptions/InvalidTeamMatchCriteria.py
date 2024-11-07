class InvalidTeamMatchCriteria(Exception):
    def __init__(self, message):            
        # Call the base class constructor with the parameters it needs
        print(message)
        super().__init__(message)