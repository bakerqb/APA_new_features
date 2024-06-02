from .PlayerResult import PlayerResult
from dataClasses.eightBall.EightBallScore import EightBallScore
from dataClasses.nineBall.NineBallScore import NineBallScore
from dataClasses.Team import Team
from src.srcMain.Database import Database
from dataClasses.Player import Player


class IPlayerMatch:
    def initWithDiv(self, matchDiv, team1: Team, team2: Team, playerMatchId: int, teamMatchId: int, datePlayed):
        pass

    def initWithDirectInfo(self, playerMatchId, teamMatchId, player_name1, team1, skill_level1, match_pts_earned1, games_won1, games_needed1,
                   player_name2, team2, skill_level2, match_pts_earned2, games_won2, games_needed2, datePlayed, isEightBall):
        db = Database()
        
        score1 = {}
        score2 = {}
        if isEightBall:
            score1 = EightBallScore(match_pts_earned1, games_won1, games_needed1)
            score2 = EightBallScore(match_pts_earned2, games_won2, games_needed2)
        else:
            score1 = NineBallScore(match_pts_earned1, games_won1, games_needed1)
            score2 = NineBallScore(match_pts_earned2, games_won2, games_needed2)

        self.playerResults = []
        
        # TODO: Figure out how to find the memberId/currentSkillLevel of a player who once belonged to a team but no longer does
        player1Info = db.getPlayerBasedOnTeamIdAndPlayerName(team1.toJson().get('teamId'), player_name1)
        if player1Info is None:
            return None
        memberId1, playerName1, currentSkillLevel1 = player1Info
        player1 = Player(memberId1, playerName1, currentSkillLevel1)
        
        player2Info = db.getPlayerBasedOnTeamIdAndPlayerName(team2.toJson().get('teamId'), player_name2)
        if player2Info is None:
            return None
        memberId2, playerName2, currentSkillLevel2 = player2Info
        player2 = Player(memberId2, playerName2, currentSkillLevel2)

        self.playerResults.append(PlayerResult(team1, player1, skill_level1, score1))
        self.playerResults.append(PlayerResult(team2, player2, skill_level2, score2))
        self.playerMatchId = playerMatchId
        self.teamMatchId = teamMatchId
        self.datePlayed = datePlayed
        return self
    
    def initNormal(self, playerResults, playerMatchId, teamMatchId, datePlayed):
        self.playerResults = playerResults
        self.playerMatchId = playerMatchId
        self.teamMatchId = teamMatchId
        self.datePlayed = datePlayed

    def getPlayerMatchResult(self):
        return self.playerResults
    
    def getPlayerMatchId(self):
        return self.playerMatchId
    
    def getTeamMatchId(self):
        return self.teamMatchId
    
    def isPlayedBy(self, player: Player):
        for playerResult in self.playerResults:
            if playerResult.toJson().get('player').get('playerName') == player.toJson().get('playerName'):
                return True
        return False

    def proper_playerResult_order_with_player(self, player: Player):
        if (self.playerResults[0].toJson().get('player') != player.toJson()):
            self.playerResults.reverse()

    def proper_playerResult_order_with_team(self, team_in_question):
        if (self.playerResults[0].get_team_name() != team_in_question):
            self.playerResults.reverse()

    def toJson(self):
        return {
            "playerResults": list(map(lambda playerResult: playerResult.toJson(), self.playerResults)),
            "playerMatchId": self.playerMatchId,
            "teamMatchId": self.teamMatchId,
            "datePlayed": self.datePlayed
        }