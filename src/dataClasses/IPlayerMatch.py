class IPlayerMatch:
    def getPlayerMatchResult(self):
        return self.playerResults
    
    def getPlayerMatchId(self):
        return self.playerMatchId
    
    def getTeamMatchId(self):
        return self.teamMatchId
    
    def isPlayedBy(self, player_name: str):
        for playerResult in self.playerResults:
            if not player_name or player_name == playerResult.get_player_name():
                return True
        return False

    def proper_playerResult_order_with_player(self, player_in_question):
        if (self.playerResults[0].get_player_name() != player_in_question):
            self.playerResults.reverse()

    def proper_playerResult_order_with_team(self, team_in_question):
        if (self.playerResults[0].get_team_name() != team_in_question):
            self.playerResults.reverse()