from .PlayerResult import PlayerResult
from dataClasses.eightBall.EightBallScore import EightBallScore
from dataClasses.nineBall.NineBallScore import NineBallScore
from dataClasses.Team import Team
from src.srcMain.Database import Database
from dataClasses.Player import Player
from datetime import datetime


class IPlayerMatch:
    def initWithDiv(self, matchDiv, team1: Team, team2: Team, playerMatchId: int, teamMatchId: int, datePlayed):
        pass

    def initWithDirectInfo(self, playerMatchId, teamMatchId, playerName1, team1, skillLevel1, matchPtsEarned1, gamesWon1, gamesNeeded1,
                   playerName2, team2, skillLevel2, matchPtsEarned2, gamesWon2, gamesNeeded2, datePlayed, isEightBall):
        db = Database()
        
        score1 = {}
        score2 = {}
        if isEightBall:
            score1 = EightBallScore(matchPtsEarned1, gamesWon1, gamesNeeded1)
            score2 = EightBallScore(matchPtsEarned2, gamesWon2, gamesNeeded2)
        else:
            score1 = NineBallScore(matchPtsEarned1, gamesWon1, gamesNeeded1)
            score2 = NineBallScore(matchPtsEarned2, gamesWon2, gamesNeeded2)

        self.playerResults = []
        
        # TODO: Figure out how to find the memberId/currentSkillLevel of a player who once belonged to a team but no longer does
        player1Info = db.getPlayerBasedOnTeamIdAndPlayerName(team1.toJson().get('teamId'), playerName1)
        if player1Info is None:
            return None
        memberId1, playerName1, currentSkillLevel1 = player1Info
        player1 = Player(memberId1, playerName1, currentSkillLevel1)
        
        player2Info = db.getPlayerBasedOnTeamIdAndPlayerName(team2.toJson().get('teamId'), playerName2)
        if player2Info is None:
            return None
        memberId2, playerName2, currentSkillLevel2 = player2Info
        player2 = Player(memberId2, playerName2, currentSkillLevel2)

        self.playerResults.append(PlayerResult(team1, player1, skillLevel1, score1))
        self.playerResults.append(PlayerResult(team2, player2, skillLevel2, score2))
        self.playerMatchId = playerMatchId
        self.teamMatchId = teamMatchId
        self.datePlayed = self.toReadableDateTimeString(datePlayed)
        return self
    
    def initNormal(self, playerResults, playerMatchId, teamMatchId, datePlayed):
        self.playerResults = playerResults
        self.playerMatchId = playerMatchId
        self.teamMatchId = teamMatchId
        self.datePlayed = self.toReadableDateTimeString(datePlayed)

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

    def properPlayerResultOrderWithPlayer(self, player: Player):
        if (self.playerResults[0].toJson().get('player') != player.toJson()):
            self.playerResults.reverse()

    def toReadableDateTimeString(self, date):
        return datetime.strptime(date, "%Y-%m-%d").strftime("%B %-d, %Y")


    def toJson(self):
        return {
            "playerResults": list(map(lambda playerResult: playerResult.toJson(), self.playerResults)),
            "playerMatchId": self.playerMatchId,
            "teamMatchId": self.teamMatchId,
            "datePlayed": self.datePlayed
        }