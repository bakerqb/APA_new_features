import sqlite3
from tabulate import tabulate
from Config import Config
import statistics

class Database:
    ############### Helper functions ###############
    def __init__(self):
        self.con = sqlite3.connect("results.db")
        self.cur = self.con.cursor()
        self.config = Config().getConfig()
    
    def getGame(self, isEightBall):
        return 'Eight' if isEightBall else 'Nine'
    
    def getMedian(self, scores):
        nums = []
        for item in scores:
            nums.append(item[0])
        return statistics.median(nums)
    
    ############### Game agnostic functions ###############
    def deleteSessionData(self):
        sessionSeason = self.config.get('session_season_in_question')
        sessionYear = self.config.get('session_year_in_question')
        game = self.config.get('game')
        game = self.getGame(game == '8-ball')

        self.cur.execute("DELETE FROM {}BallPlayerMatch AS p WHERE p.teamMatchId IN (SELECT t.teamMatchId FROM {}BallTeamMatch AS t WHERE t.sessionSeason = '{}' AND t.sessionYear = {})".format(game, game, sessionSeason, str(sessionYear)))
        self.cur.execute("DELETE FROM {}BallTeamMatch WHERE sessionSeason = '{}' AND sessionYear = {}".format(game, sessionSeason, str(sessionYear)))
        self.con.commit()
    
    def refreshAllNineBallTables(self, isEightBall):
        self.dropTables(isEightBall)
        self.createTables(isEightBall)
    
    def dropTables(self, isEightBall):
        game = self.getGame(isEightBall)

        try:
            self.cur.execute("DROP TABLE {}BallPlayerMatch".format(game))
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE {}BallScore".format(game))
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE {}BallDivision".format(game))
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE {}BallTeamMatch".format(game))
        except Exception:
            pass

        self.con.commit()

    def createTables(self, isEightBall):
        game = self.getGame(isEightBall)
        self.cur.execute(
            "CREATE TABLE {}BallTeamMatch (".format(game) +
            "teamMatchId INTEGER PRIMARY KEY, datePlayed DATETIME, " +
            "sessionSeason TEXT CHECK(sessionSeason IN ('SPRING', 'SUMMER', 'FALL')), " + 
            "sessionYear INTEGER)"
        )

        self.cur.execute(
            "CREATE TABLE {}BallPlayerMatch(".format(game) +
            "playerMatchId INTEGER, teamMatchId INTEGER, team_name1 varchar(255), " +
            "player_name1 varchar(255), skill_level1 int, scoreId1 INTEGER, " + 
            "team_name2 varchar(255), player_name2 varchar(255), " +
            "skill_level2 INTEGER, scoreId2 INTEGER, PRIMARY KEY (playerMatchId, teamMatchId))"
        )

        self.cur.execute(
            "CREATE TABLE {}BallDivision(divisionLink varchar(255) PRIMARY KEY)".format(game)
        )

        self.cur.execute(
            "CREATE TABLE {}BallScore(".format(game) +
            "scoreId INTEGER PRIMARY KEY AUTOINCREMENT, match_pts_earned INTEGER, ball_pts_earned INTEGER, " +
            "ball_pts_needed INTEGER)"
        )
        
        self.con.commit()

    def addDivisionValue(self, link, isEightBall):
        game = self.getGame(isEightBall)
        # Checks if value already exists in DB, and if not, adds it to DB
        if not self.isValueInDivisionTable(link, isEightBall):
            self.cur.execute("""INSERT INTO {}BallDivision VALUES ("{}")""".format(game, link))
            self.con.commit()

    def isValueInDivisionTable(self, link, isEightBall):
        game = self.getGame(isEightBall)
        return self.cur.execute("SELECT COUNT(*) FROM {}BallDivision WHERE divisionLink='{}'".format(game, link)).fetchone()[0] > 0

    def isValueInTeamMatchTable(self, teamMatchId, isEightBall):
        game = self.getGame(isEightBall)
        return self.cur.execute("SELECT COUNT(*) FROM {}BallTeamMatch WHERE teamMatchId = {}".format(game, teamMatchId)).fetchone()[0] > 0

    def addTeamMatchValue(self, teamMatchId, apa_datetime, sessionSeason, sessionYear, isEightBall):
        try:
            game = self.getGame(isEightBall)
            self.cur.execute("INSERT INTO {}BallTeamMatch VALUES ({}, '{}', '{}', {})".format(game, teamMatchId, apa_datetime, sessionSeason, sessionYear))
            self.con.commit()
        except Exception:
            pass

    def countPlayerMatches(self, isEightBall):
        game = self.getGame(isEightBall)
        return self.cur.execute("SELECT COUNT(*) FROM {}BallPlayerMatch".format(game)).fetchone()[0]
    
    def countTeamMatches(self, isEightBall):
        game = self.getGame(isEightBall)
        return self.cur.execute("SELECT COUNT(*) FROM {}BallTeamMatch".format(game)).fetchone()[0]
    
    def addPlayerMatchValue(self, playerMatch, isEightBall):
        game = self.getGame(isEightBall)
        for playerResult in playerMatch.getPlayerMatchResult():
            self.cur.execute(self.formatScoreInsertQuery(playerResult.get_score(), isEightBall))

        scoreId = int(self.cur.execute("SELECT last_insert_rowid() FROM NineBallScore").fetchone()[0])
        
        player_match_id = playerMatch.getPlayerMatchId()
        team_match_id = playerMatch.getTeamMatchId()
        team_name_1 = playerMatch.getPlayerMatchResult()[0].get_team_name().replace('"', '\'')
        player_name1 = playerMatch.getPlayerMatchResult()[0].get_player_name().replace('"', '\'')
        skill_level1 = str(playerMatch.getPlayerMatchResult()[0].get_skill_level())
        score_id1 = str(scoreId-1)
        team_name_2 = playerMatch.getPlayerMatchResult()[1].get_team_name().replace('"', '\'')
        player_name2 = playerMatch.getPlayerMatchResult()[1].get_player_name().replace('"', '\'')
        skill_level2 = str(playerMatch.getPlayerMatchResult()[1].get_skill_level())
        score_id2 = str(scoreId)


        self.cur.execute(
            f"""INSERT INTO {game}BallPlayerMatch VALUES ({player_match_id}, {team_match_id}, "{team_name_1}", "{player_name1}", {skill_level1}, {score_id1}, "{team_name_2}", "{player_name2}", {skill_level2}, {score_id2})"""
        )
        self.con.commit()

    def formatScoreInsertQuery(self, score, isEightBall):
        if isEightBall:
            return "INSERT INTO EightBallScore VALUES ({}, {}, {}, {})".format(
                "NULL", 
                str(score.get_match_pts_earned()), 
                str(score.get_games_won()), 
                str(score.get_games_needed())
            )
        else:
            return "INSERT INTO NineBallScore VALUES ({}, {}, {}, {})".format(
                "NULL", 
                str(score.get_match_pts_earned()), 
                str(score.get_ball_pts_earned()), 
                str(score.get_ball_pts_needed())
            )
        
    def getTeamRoster(self, sessionSeason, sessionYear, teamName, isEightBall):
        gamePrefix = "Eight" if isEightBall else "Nine"
        teamName = teamName.replace('"', '\'')
        players = self.cur.execute(
            "SELECT DISTINCT playerName FROM " +
                """(SELECT n.player_name1 AS playerName FROM {}BallPlayerMatch n LEFT JOIN {}BallTeamMatch t ON n.teamMatchId = t.teamMatchId WHERE team_name1 = "{}" AND sessionSeason = "{}" AND sessionYear = {} """.format(gamePrefix, gamePrefix, teamName, sessionSeason, sessionYear) +
                "UNION " +
                """SELECT n.player_name2 AS playerName FROM {}BallPlayerMatch n LEFT JOIN {}BallTeamMatch t ON n.teamMatchId = t.teamMatchId WHERE team_name2 = "{}" AND sessionSeason = "{}" AND sessionYear = {})""".format(gamePrefix, gamePrefix, teamName, sessionSeason, sessionYear)
        ).fetchall()
        roster = []
        for player in players:
            roster.append(player[0])
        return roster
    
    def getDatePlayed(self, teamMatchId: int, isEightBall: bool):
        gamePrefix = "Eight" if isEightBall else "Nine"
        return self.cur.execute(
            "SELECT datePlayed FROM {}BallTeamMatch WHERE teamMatchId = {}".format(gamePrefix, str(teamMatchId))
        ).fetchone()[0]

    
    ############### 9 Ball functions ###############
    def isNineBallDivisionTableFull(self, count):
        return self.cur.execute("SELECT COUNT(*) FROM NineBallDivision").fetchone()[0] >= count
        
    def getNineBallDivisionLinks(self):
        return self.cur.execute("SELECT * FROM NineBallDivision").fetchall()
    
    def createNineBallMatrix(self):
        matrix = []
        matrix.append([])
        for i in range(0, 10):
            matrix[0].append(i)
        for i in range(1, 10):
            matrix.append([i, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        for i in range(1, 10):
            for j in range(i+1, 10):
                matches_low_against_high = self.cur.execute(
                    "SELECT SUM(score1.match_pts_earned) AS total_pts1, " +
                    "SUM(score2.match_pts_earned) AS total_pts2, COUNT(*) " + 
                    "FROM NineBallPlayerMatch n " +
                    "LEFT JOIN NineBallScore score1 " +
                    "ON score1.scoreId = n.scoreId1 " +
                    "LEFT JOIN NineBallScore score2 " +
                    "ON score2.scoreId = n.scoreId2 " +
                    "WHERE n.skill_level1 = {} AND n.skill_level2 = {}".format(i, j)
                ).fetchone()

                matches_high_against_low = self.cur.execute(
                    "SELECT SUM(score1.match_pts_earned) AS total_pts1, " +
                    "SUM(score2.match_pts_earned) AS total_pts2, COUNT(*) " + 
                    "FROM NineBallPlayerMatch n " +
                    "LEFT JOIN NineBallScore score1 " +
                    "ON score1.scoreId = n.scoreId1 " +
                    "LEFT JOIN NineBallScore score2 " +
                    "ON score2.scoreId = n.scoreId2 " +
                    "WHERE n.skill_level1 = {} AND n.skill_level2 = {}".format(j, i)
                ).fetchone()

                games = matches_low_against_high[2] + matches_high_against_low[2]
                if games > 0:
                    pts_from_lower_rated_player = (matches_low_against_high[0] if matches_low_against_high[0] else 0)  + (matches_high_against_low[1] if matches_high_against_low[1] else 0)
                    pts_from_higher_rated_player = (matches_low_against_high[1] if matches_low_against_high[1] else 0) + (matches_high_against_low[0] if matches_high_against_low[0] else 0)
                    matrix[i][j] = str(round(pts_from_lower_rated_player/games, 1)) + " pts expected\n" + str(games) + " games"
                    matrix[j][i] = str(round(pts_from_higher_rated_player/games, 1)) + " pts expected\n" + str(games) + " games"
        
        print(tabulate(matrix, headers="firstrow", tablefmt="fancy_grid"))


    def createNineBallMatrixMedian(self):
        matrix = []
        matrix.append([])
        for i in range(0, 10):
            matrix[0].append(i)
        for i in range(1, 10):
            matrix.append([i, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        for i in range(1, 10):
            for j in range(i+1, 10):
                scores = self.cur.execute("SELECT lower_level_pts FROM "
                    "(SELECT score1.match_pts_earned AS lower_level_pts, " +
                    "score2.match_pts_earned AS higher_level_pts " + 
                    "FROM NineBallPlayerMatch n " +
                    "LEFT JOIN NineBallScore score1 " +
                    "ON score1.scoreId = n.scoreId1 " +
                    "LEFT JOIN NineBallScore score2 " +
                    "ON score2.scoreId = n.scoreId2 " +
                    "WHERE n.skill_level1 = {} AND n.skill_level2 = {} ".format(i, j) +
                    "UNION ALL SELECT score1.match_pts_earned AS higher_level_pts, " +
                    "score2.match_pts_earned AS lower_level_pts " + 
                    "FROM NineBallPlayerMatch n " +
                    "LEFT JOIN NineBallScore score1 " +
                    "ON score1.scoreId = n.scoreId1 " +
                    "LEFT JOIN NineBallScore score2 " +
                    "ON score2.scoreId = n.scoreId2 " +
                    "WHERE n.skill_level1 = {} AND n.skill_level2 = {}) ".format(j, i) +
                    "ORDER BY lower_level_pts"
                ).fetchall()

                numGames = len(scores)
                if numGames > 0:
                    median = round(self.getMedian(scores), 0)
                    matrix[i][j] = str(median) + " pts expected\n" + str(numGames) + " games"
                    matrix[j][i] = str(20 - median) + " pts expected\n" + str(numGames) + " games"
        
        print(tabulate(matrix, headers="firstrow", tablefmt="fancy_grid"))

    def getNineBallPlayerMatchesOfPlayer(self, playerName):
        playerName = playerName.replace('"', '\'')
        
        return self.cur.execute(
            "SELECT n.player_name1, n.skill_level1, score1.match_pts_earned, " + 
            "n.player_name2, n.skill_level2, score2.match_pts_earned, t.datePlayed " + 
            "FROM NineBallPlayerMatch n " +
            "LEFT JOIN NineBallTeamMatch t " + 
            "ON n.teamMatchId = t.teamMatchId " +
            "LEFT JOIN NineBallScore score1 " +
            "ON score1.scoreId = n.scoreId1 " +
            "LEFT JOIN NineBallScore score2 " +
            "ON score2.scoreId = n.scoreId2 " +
            """WHERE (n.player_name1 = "{}" OR n.player_name2 = "{}") """.format(playerName, playerName) +
            "AND DATEADD(year,-1,GETDATE())"
        )
    
    def getTeamResults(self, sessionSeason, sessionYear, teamName, isEightBall):
        game = self.getGame(isEightBall)
        return self.cur.execute(
            "SELECT n.playerMatchId, n.teamMatchId, n.player_name1, " +
            "n.team_name1, n.skill_level1, score1.match_pts_earned, score1.ball_pts_earned, score1.ball_pts_needed, " + 
            "n.player_name2, " +
            "n.team_name2, n.skill_level2, score2.match_pts_earned, score2.ball_pts_earned, score2.ball_pts_needed, t.datePlayed " + 
            "FROM {}BallPlayerMatch n ".format(game) +
            "LEFT JOIN {}BallTeamMatch t ".format(game) + 
            "ON n.teamMatchId = t.teamMatchId " +
            "LEFT JOIN {}BallScore score1 ".format(game) +
            "ON score1.scoreId = n.scoreId1 " +
            "LEFT JOIN {}BallScore score2 ".format(game) +
            "ON score2.scoreId = n.scoreId2 " +
            """WHERE (n.team_name1 = "{}" OR n.team_name2 = "{}") """.format(teamName, teamName) +
            "AND t.sessionSeason = '{}' AND t.sessionYear = {} ".format(sessionSeason, sessionYear) +
            "ORDER BY t.datePlayed"
        ).fetchall()
    
    def getNineBallPlayersAboveSkillLevel(self, skill_level):
        return self.cur.execute(
            "SELECT DISTINCT playerName, skillLevel, MAX(datePlayed) FROM " +
                """(SELECT n.player_name1 as playerName, n.skill_level1 as skillLevel, t.datePlayed FROM NineBallPlayerMatch n LEFT JOIN NineBallTeamMatch t ON n.teamMatchId = t.teamMatchId WHERE n.skill_level1 > {} """.format(skill_level) +
                "UNION " +
                """SELECT n.player_name2 as playerName, n.skill_level2 as skillLevel, t.datePlayed FROM NineBallPlayerMatch n LEFT JOIN NineBallTeamMatch t ON n.teamMatchId = t.teamMatchId WHERE n.skill_level2 > {}) GROUP BY playerName ORDER BY datePlayed""".format(skill_level)
        ).fetchall()

    def getNineBallPlayerMatchesBetweenSkillLevels(self, skill_level1, skill_level2):
        return self.cur.execute(
             "SELECT n.playerMatchId, n.teamMatchId, n.player_name1, " +
            "n.team_name1, n.skill_level1, score1.match_pts_earned, score1.ball_pts_earned, score1.ball_pts_needed, " + 
            "n.player_name2, " +
            "n.team_name2, n.skill_level2, score2.match_pts_earned, score2.ball_pts_earned, score2.ball_pts_needed, t.datePlayed " + 
            "FROM NineBallPlayerMatch n " +
            "LEFT JOIN NineBallTeamMatch t " + 
            "ON n.teamMatchId = t.teamMatchId " +
            "LEFT JOIN NineBallScore score1 " +
            "ON score1.scoreId = n.scoreId1 " +
            "LEFT JOIN NineBallScore score2 " +
            "ON score2.scoreId = n.scoreId2 " +
            "WHERE (n.skill_level1 = {} AND n.skill_level2 = {}) ".format(skill_level1, skill_level2) +
            "OR (n.skill_level1 = {} AND n.skill_level2 = {}) ".format(skill_level2, skill_level1) +
            "ORDER BY t.datePlayed"
        ).fetchall()
    
    def getRubbishMatches(self):
        return self.cur.execute(
             "SELECT n.player_name1, " +
            "n.team_name1, n.skill_level1, score1.match_pts_earned, score1.ball_pts_earned, score1.ball_pts_needed, " + 
            "n.player_name2, " +
            "n.team_name2, n.skill_level2, score2.match_pts_earned, score2.ball_pts_earned, score2.ball_pts_needed, t.datePlayed " + 
            "FROM NineBallPlayerMatch n " +
            "LEFT JOIN NineBallTeamMatch t " + 
            "ON n.teamMatchId = t.teamMatchId " +
            "LEFT JOIN NineBallScore score1 " +
            "ON score1.scoreId = n.scoreId1 " +
            "LEFT JOIN NineBallScore score2 " +
            "ON score2.scoreId = n.scoreId2 " +
            "WHERE score1.ball_pts_earned = 0 OR score2.ball_pts_earned = 0 " +
            "ORDER BY t.datePlayed"
        ).fetchall()



    ############### 8 Ball functions ###############

    def deleteEightBallTeamMatch(self, teamMatchId):
        self.cur.execute("DELETE FROM EightBallTeamMatch WHERE teamMatchId = {}".format(teamMatchId))
        self.con.commit()
    
    
    def getEightBallDivisionLinks(self):
        return self.cur.execute("SELECT * FROM EightBallDivision").fetchall()