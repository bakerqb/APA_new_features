import dataClasses.IScore as IScore
import dataClasses.Team as Team
import dataClasses.Player as Player

class PlayerResult:
    def __init__(self, team: Team, player: Player, skill_level: int, score: IScore):
        self.team = team
        self.player = player
        self.skill_level = skill_level
        self.score = score

    def toJson(self):
        return {
            "team": self.team.toJson(),
            "player": self.player.toJson(),
            "skill_level": self.skill_level,
            "score": self.score.toJson()
        }