import sqlite3
from tabulate import tabulate
from Config import Config
import statistics

class Database:
    def __init__(self):
        self.con = sqlite3.connect("results.db")
        self.cur = self.con.cursor()
        self.config = Config().getConfig()

    ############### 9 Ball functions ###############
    def deleteNineBallSeason(self):
        sessionSeason = self.config.get('session_season_in_question')
        sessionYear = self.config.get('session_year_in_question')
        self.cur.execute("DELETE FROM NineBallPlayerMatch AS p WHERE p.teamMatchId IN (SELECT t.teamMatchId FROM NineBallTeamMatch AS t WHERE t.sessionSeason = '{}' AND t.sessionYear = {})".format(sessionSeason, str(sessionYear)))
        self.cur.execute("DELETE FROM NineBallTeamMatch WHERE sessionSeason = '{}' AND sessionYear = {}".format(sessionSeason, str(sessionYear)))
        self.con.commit()
    
    def refreshAllNineBallTables(self):
        self.dropNineBallTables()
        self.createNineBallTables()
    
    def dropNineBallTables(self):
        try:
            self.cur.execute("DROP TABLE NineBallPlayerMatch")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE NineBallScore")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE NineBallDivision")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE NineBallTeamMatch")
        except Exception:
            pass

        self.con.commit()

    def createNineBallTables(self):
        self.cur.execute(
            "CREATE TABLE NineBallTeamMatch (" +
            "teamMatchId INTEGER PRIMARY KEY, datePlayed DATETIME, " +
            "sessionSeason TEXT CHECK(sessionSeason IN ('SPRING', 'SUMMER', 'FALL')), " + 
            "sessionYear INTEGER)"
        )


        self.cur.execute(
            "CREATE TABLE NineBallPlayerMatch(" +
            "playerMatchId INTEGER, teamMatchId INTEGER, team_name1 varchar(255), " +
            "player_name1 varchar(255), skill_level1 int, scoreId1 INTEGER, " + 
            "team_name2 varchar(255), player_name2 varchar(255), " +
            "skill_level2 INTEGER, scoreId2 INTEGER, PRIMARY KEY (playerMatchId, teamMatchId))"
        )

        self.cur.execute(
            "CREATE TABLE NineBallScore(" +
            "scoreId INTEGER PRIMARY KEY AUTOINCREMENT, match_pts_earned INTEGER, ball_pts_earned INTEGER, " +
            "ball_pts_needed INTEGER)"
        )

        self.cur.execute(
            "CREATE TABLE NineBallDivision(divisionLink varchar(255) PRIMARY KEY)"
        )
        
        self.con.commit()

    def addNineBallDivisionValue(self, link):
        # Checks if value already exists in DB, and if not, adds it to DB
        if not self.isValueInNineBallDivisionTable(link):
            self.cur.execute("""INSERT INTO NineBallDivision VALUES ("{}")""".format(link))
            self.con.commit()

    def isValueInNineBallDivisionTable(self, link):
        return self.cur.execute("SELECT COUNT(*) FROM NineBallDivision WHERE divisionLink='{}'".format(link)).fetchone()[0] > 0


    def isNineBallDivisionTableFull(self, count):
        return self.cur.execute("SELECT COUNT(*) FROM NineBallDivision").fetchone()[0] >= count
    
    def isValueInNineBallTeamMatchTable(self, teamMatchId):
        return self.cur.execute("SELECT COUNT(*) FROM NineBallTeamMatch WHERE teamMatchId = {}".format(teamMatchId)).fetchone()[0] > 0
    
    def addNineBallTeamMatchValue(self, teamMatchId, apa_datetime, sessionSeason, sessionYear):
        try:
            self.cur.execute("INSERT INTO NineBallTeamMatch VALUES ({}, '{}', '{}', {})".format(teamMatchId, apa_datetime, sessionSeason, sessionYear))
            self.con.commit()
        except Exception:
            pass

    def countNineBallPlayerMatch(self):
        return self.cur.execute("SELECT COUNT(*) FROM NineBallPlayerMatch").fetchone()[0]
    
    def countNineBallTeamMatch(self):
        return self.cur.execute("SELECT COUNT(*) FROM NineBallTeamMatch").fetchone()[0]
    
    def addNineBallPlayerMatchValue(self, playerMatch):
        for playerResult in playerMatch.getPlayerMatchResult():
            self.cur.execute(self.formatNineBallScoreInsertQuery(playerResult.get_score()))
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
            f"""INSERT INTO NineBallPlayerMatch VALUES ({player_match_id}, {team_match_id}, "{team_name_1}", "{player_name1}", {skill_level1}, {score_id1}, "{team_name_2}", "{player_name2}", {skill_level2}, {score_id2})"""
        )
        self.con.commit()

    def formatNineBallScoreInsertQuery(self, score):
        return "INSERT INTO NineBallScore VALUES ({}, {}, {}, {})".format(
            "NULL", 
            str(score.get_match_pts_earned()), 
            str(score.get_ball_pts_earned()), 
            str(score.get_ball_pts_needed())
        )
    
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
    
    def getNineBallTeamResults(self, sessionSeason, sessionYear, teamName):
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
            """WHERE (n.team_name1 = "{}" OR n.team_name2 = "{}") """.format(teamName, teamName) +
            "AND t.sessionSeason = '{}' AND t.sessionYear = {} ".format(sessionSeason, sessionYear) +
            "ORDER BY t.datePlayed"
        ).fetchall()
    
    def getNineBallRoster(self, sessionSeason, sessionYear, teamName):
        teamName = teamName.replace('"', '\'')
        return self.cur.execute(
            "SELECT DISTINCT playerName FROM " +
                """(SELECT n.player_name1 AS playerName FROM NineBallPlayerMatch n LEFT JOIN NineBallTeamMatch t ON n.teamMatchId = t.teamMatchId WHERE team_name1 = "{}" AND sessionSeason = "{}" AND sessionYear = {} """.format(teamName, sessionSeason, sessionYear) +
                "UNION " +
                """SELECT n.player_name2 AS playerName FROM NineBallPlayerMatch n LEFT JOIN NineBallTeamMatch t ON n.teamMatchId = t.teamMatchId WHERE team_name2 = "{}" AND sessionSeason = "{}" AND sessionYear = {})""".format(teamName, sessionSeason, sessionYear)
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

    
    
    def deleteEightBallSeason(self):
        sessionSeason = self.config.get('session_season_in_question')
        sessionYear = self.config.get('session_year_in_question')
        self.cur.execute("DELETE FROM EightBallPlayerMatch AS p WHERE p.teamMatchId IN (SELECT t.teamMatchId FROM EightBallTeamMatch AS t WHERE t.sessionSeason = '{}' AND t.sessionYear = {})".format(sessionSeason, str(sessionYear)))
        self.cur.execute("DELETE FROM EightBallTeamMatch WHERE sessionSeason = '{}' AND sessionYear = {}".format(sessionSeason, str(sessionYear)))
        self.con.commit()

    

    def refreshAllEightBallTables(self):
        self.dropEightBallTables()
        self.createEightBallTables()
    
    def dropEightBallTables(self):
        try:
            self.cur.execute("DROP TABLE EightBallPlayerMatch")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE EightBallScore")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE EightBallDivision")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE EightBallTeamMatch")
        except Exception:
            pass

        self.con.commit()

    def createEightBallTables(self):
        self.cur.execute(
            "CREATE TABLE EightBallTeamMatch (" +
            "teamMatchId INTEGER PRIMARY KEY, datePlayed DATETIME, " +
            "sessionSeason TEXT CHECK(sessionSeason IN ('SPRING', 'SUMMER', 'FALL')), " + 
            "sessionYear INTEGER)"
        )


        self.cur.execute(
            "CREATE TABLE EightBallPlayerMatch(" +
            "playerMatchId INTEGER, teamMatchId INTEGER, team_name1 varchar(255), " +
            "player_name1 varchar(255), skill_level1 int, scoreId1 INTEGER, " + 
            "team_name2 varchar(255), player_name2 varchar(255), " +
            "skill_level2 INTEGER, scoreId2 INTEGER, PRIMARY KEY (playerMatchId, teamMatchId))"
        )

        self.cur.execute(
            "CREATE TABLE EightBallScore(" +
            "scoreId INTEGER PRIMARY KEY AUTOINCREMENT, match_pts_earned INTEGER, ball_pts_earned INTEGER, " +
            "ball_pts_needed INTEGER)"
        )

        self.cur.execute(
            "CREATE TABLE EightBallDivision(divisionLink varchar(255) PRIMARY KEY)"
        )
        
        self.con.commit()
    
    def addEightBallDivisionValue(self, link):
        # Checks if value already exists in DB, and if not, adds it to DB
        if not self.isValueInEightBallDivisionTable(link):
            self.cur.execute("""INSERT INTO EightBallDivision VALUES ("{}")""".format(link))
            self.con.commit()

    def isValueInEightBallDivisionTable(self, link):
        return self.cur.execute("SELECT COUNT(*) FROM EightBallDivision WHERE divisionLink='{}'".format(link)).fetchone()[0] > 0

    def isValueInEightBallTeamMatchTable(self, teamMatchId):
        return self.cur.execute("SELECT COUNT(*) FROM EightBallTeamMatch WHERE teamMatchId = {}".format(teamMatchId)).fetchone()[0] > 0
    
    def isEightBallDivisionTableFull(self, count):
        return self.cur.execute("SELECT COUNT(*) FROM EightBallDivision").fetchone()[0] >= count
    
    def addEightBallTeamMatchValue(self, teamMatchId, apa_datetime, sessionSeason, sessionYear):
        try:
            self.cur.execute("INSERT INTO EightBallTeamMatch VALUES ({}, '{}', '{}', {})".format(teamMatchId, apa_datetime, sessionSeason, sessionYear))
            self.con.commit()
        except Exception:
            pass

    def countEightBallPlayerMatch(self):
        return self.cur.execute("SELECT COUNT(*) FROM EightBallPlayerMatch").fetchone()[0]
    
    def countEightBallTeamMatch(self):
        return self.cur.execute("SELECT COUNT(*) FROM EightBallTeamMatch").fetchone()[0]
    
    def addEightBallPlayerMatchValue(self, playerMatch):
        for playerResult in playerMatch.getPlayerMatchResult():
            self.cur.execute(self.formatEightBallScoreInsertQuery(playerResult.get_score()))
        scoreId = int(self.cur.execute("SELECT last_insert_rowid() FROM EightBallScore").fetchone()[0])
        
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
            f"""INSERT INTO EightBallPlayerMatch VALUES ({player_match_id}, {team_match_id}, "{team_name_1}", "{player_name1}", {skill_level1}, {score_id1}, "{team_name_2}", "{player_name2}", {skill_level2}, {score_id2})"""
        )
        self.con.commit()

    def formatEightBallScoreInsertQuery(self, score):
        return "INSERT INTO EightBallScore VALUES ({}, {}, {}, {})".format(
            "NULL", 
            str(score.get_match_pts_earned()), 
            str(score.get_games_won()), 
            str(score.get_games_needed())
        )
    
    def getEightBallDivisionLinks(self):
        return self.cur.execute("SELECT * FROM EightBallDivision").fetchall()
    
    def getEightBallTeamResults(self, sessionSeason, sessionYear, teamName):
        return self.cur.execute(
            "SELECT n.playerMatchId, n.teamMatchId, n.player_name1, " +
            "n.team_name1, n.skill_level1, score1.match_pts_earned, score1.ball_pts_earned, score1.ball_pts_needed, " + 
            "n.player_name2, " +
            "n.team_name2, n.skill_level2, score2.match_pts_earned, score2.ball_pts_earned, score2.ball_pts_needed, t.datePlayed " + 
            "FROM EightBallPlayerMatch n " +
            "LEFT JOIN EightBallTeamMatch t " + 
            "ON n.teamMatchId = t.teamMatchId " +
            "LEFT JOIN EightBallScore score1 " +
            "ON score1.scoreId = n.scoreId1 " +
            "LEFT JOIN EightBallScore score2 " +
            "ON score2.scoreId = n.scoreId2 " +
            """WHERE (n.team_name1 = "{}" OR n.team_name2 = "{}") """.format(teamName, teamName) +
            "AND t.sessionSeason = '{}' AND t.sessionYear = {} ".format(sessionSeason, sessionYear) +
            "ORDER BY t.datePlayed"
        ).fetchall()
    
    def getEightBallRoster(self, sessionSeason, sessionYear, teamName):
        teamName = teamName.replace('"', '\'')
        return self.cur.execute(
            "SELECT DISTINCT playerName FROM " +
                """(SELECT n.player_name1 AS playerName FROM EightBallPlayerMatch n LEFT JOIN EightBallTeamMatch t ON n.teamMatchId = t.teamMatchId WHERE team_name1 = "{}" AND sessionSeason = "{}" AND sessionYear = {} """.format(teamName, sessionSeason, sessionYear) +
                "UNION " +
                """SELECT n.player_name2 AS playerName FROM EightBallPlayerMatch n LEFT JOIN EightBallTeamMatch t ON n.teamMatchId = t.teamMatchId WHERE team_name2 = "{}" AND sessionSeason = "{}" AND sessionYear = {})""".format(teamName, sessionSeason, sessionYear)
        ).fetchall()
    
    
    def getMedian(self, scores):
        nums = []
        for item in scores:
            nums.append(item[0])
        return statistics.median(nums)
