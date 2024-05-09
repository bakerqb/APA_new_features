from utils.utils import color_plain_text

class TeamResults:
    def __init__(self, teamName, sessionSeason: str, sessionYear: int, isEightBall: bool, roster: list, playerMatches: list):
        self.teamName = teamName
        self.sessionSeason = sessionSeason
        self.sessionYear = sessionYear
        self.game = "8-ball" if isEightBall else "9-ball"
        self.roster = roster
        self.playerMatchesPerPlayer = self.toPlayerMatchesPerPlayer(playerMatches)
    
    def toPlayerMatchesPerPlayer(self, playerMatches):
        playerMatchesPerPlayer = {}
        for player in self.roster:
            playerMatchesPerPlayer[player] = []

            for playerMatch in playerMatches:
                if playerMatch.isPlayedBy(player):
                    playerMatchesPerPlayer[player].append(playerMatch)
        return playerMatchesPerPlayer
    
    def toJson(self):
        return {
            "teamName": self.teamName,
            "sessionSeason": self.sessionSeason,
            "sessionYear": self.sessionYear,
            "game": self.game,
            "playerMatches": {player: list(map(lambda playerMatch: playerMatch.toJson(), playerMatches)) for player, playerMatches in self.playerMatchesPerPlayer.items()}
        }
    
    def printPlayerMatchesPerPlayer(self) -> None:
        for player in self.playerMatchesPerPlayer.keys():
            print(color_plain_text("\n-------------------- Results for {} --------------------".format(player)))
            for index, player_match in enumerate(self.playerMatchesPerPlayer[player], 1):
                print(color_plain_text("------ Match {} ------".format(str(index))))
                player_match.pretty_print(player)