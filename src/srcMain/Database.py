import sqlite3
from tabulate import tabulate
from src.srcMain.Config import Config
from src.converter.Converter import Converter
from src.dataClasses.Team import Team
import statistics

class Database:
    ############### Helper functions ###############
    def __init__(self):
        self.con = sqlite3.connect("results.db")
        self.cur = self.con.cursor()
        self.config = Config().getConfig()
        self.converter = Converter()

    
    def getGamePrefix(self, isEightBall):
        return 'Eight' if isEightBall else 'Nine'
    
    def getMedian(self, scores):
        nums = []
        for item in scores:
            nums.append(item[0])
        return statistics.median(nums)
    
    ############### Game agnostic functions ###############
    
    def addTeamInfo(self, team: Team):
        #TODO: Add team values to database
        teamData = team.toJson()
        sessionId = teamData.get('division').get('session').get('sessionId')
        divisionId = teamData.get('division').get('divisionId')
        teamId = teamData.get('teamId')
        teamNum = teamData.get('teamNum')
        teamName = teamData.get('teamName')
        self.addTeam(sessionId, divisionId, teamId, teamNum, teamName)
        
        for player in teamData.get('players'):
            memberId = player.get('memberId')
            playerName = player.get('playerName')
            currentSkillLevel = player.get('currentSkillLevel')

            self.addCurrentTeamPlayer(teamId, memberId)
            self.addPlayer(memberId, playerName, currentSkillLevel)

    def addTeam(self, sessionId: int, divisionId: int, teamId: int, teamNum: int, teamName: str):
        self.createTables(True)
        try:
            self.cur.execute(
                f"""INSERT INTO Team VALUES ({sessionId}, {divisionId}, {teamId}, {teamNum}, "{teamName}")"""
            )
        except Exception:
            pass

        self.con.commit()
        

    def addCurrentTeamPlayer(self, teamId: int, memberId: int):
        self.createTables(True)
        try:
            self.cur.execute(
                f"INSERT INTO CurrentTeamPlayer VALUES ({teamId}, {memberId})"
            )
        except Exception:
            pass
        self.con.commit()

    def addPlayer(self, memberId: int, playerName: str, currentSkillLevel: int):
        self.createTables(True)
        try:
            self.cur.execute(
                f"""INSERT INTO Player VALUES ({memberId}, "{playerName}", {currentSkillLevel})"""
            )
        except Exception:
            pass
        self.con.commit()
    
    def getDivision(self, divisionId):
        self.createTables(True)
        return self.cur.execute(
            "SELECT s.sessionId, s.sessionSeason, s.sessionYear, d.divisionId, d.divisionName, d.dayOfWeek, d.game " + 
            "FROM Division d LEFT JOIN Session s " +
            "ON d.divisionId = s.sessionId " +
            "WHERE d.divisionId = {}".format(divisionId)
        ).fetchall()
    
    def getSession(self, sessionId):
        self.createTables(True)
        return self.cur.execute("SELECT * FROM Session WHERE sessionId = {}".format(sessionId)).fetchall()
        

    def addSession(self, session):
        self.createTables(True)
        
        if self.converter.toSessionWithSql(self.getSession(session.get('sessionId'))) is None:
            self.cur.execute(f"INSERT INTO Session VALUES ({session.get('sessionId')}, '{session.get('sessionSeason')}', {session.get('sessionYear')})")
            self.con.commit()
    
    def addDivision(self, division):
        self.createTables(True)
        divisionData = division.toJson()
        session = divisionData.get('session')
        self.addSession(session)

        if self.converter.toDivisionWithSql(self.getDivision(divisionData.get('divisionId'))) is None:
            self.cur.execute(
                "INSERT INTO Division VALUES (" +
                f"{session.get('sessionId')}, " +
                f"{divisionData.get('divisionId')}, " +
                f"'{divisionData.get('divisionName')}', " + 
                f"{divisionData.get('dayOfWeek')}, " +
                f"'{divisionData.get('game')}')"
            )
            self.con.commit()
    
    def deleteSessionData(self):
        sessionSeason = self.config.get('session_season_in_question')
        sessionYear = self.config.get('session_year_in_question')
        game = self.config.get('game')
        gamePrefix = self.getGamePrefix(game == '8-ball')

        self.cur.execute("DELETE FROM {}BallPlayerMatch AS p WHERE p.teamMatchId IN (SELECT t.teamMatchId FROM {}BallTeamMatch AS t WHERE t.sessionSeason = '{}' AND t.sessionYear = {})".format(gamePrefix, gamePrefix, sessionSeason, str(sessionYear)))
        self.cur.execute("DELETE FROM {}BallTeamMatch WHERE sessionSeason = '{}' AND sessionYear = {}".format(gamePrefix, sessionSeason, str(sessionYear)))
        self.con.commit()
    
    def refreshAllTables(self, isEightBall):
        self.dropTables(isEightBall)
        self.createTables(isEightBall)
    
    def dropTables(self, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)

        try:
            self.cur.execute("DROP TABLE {}BallPlayerMatch".format(gamePrefix))
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE {}BallScore".format(gamePrefix))
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE {}BallDivision".format(gamePrefix))
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE {}BallTeamMatch".format(gamePrefix))
        except Exception:
            pass

        self.con.commit()

    def createTables(self, isEightBall):
        try:
            self.cur.execute(
                "CREATE TABLE Session (" +
                "sessionId INTEGER PRIMARY KEY, " +
                "sessionSeason TEXT CHECK(sessionSeason IN ('SPRING', 'SUMMER', 'FALL')), " + 
                "sessionYear INTEGER)"
            )
        except Exception:
            pass

        try:
            self.cur.execute(
                "CREATE TABLE Division (" +
                "sessionId INTEGER, " +
                "divisionId INTEGER, " +
                "divisionName TEXT, " + 
                "dayOfWeek INTEGER, " +
                "game TEXT, " +
                "PRIMARY KEY (sessionId, divisionId))"
            )
        except Exception:
            pass

        try:
            self.cur.execute(
                "CREATE TABLE Team (" +
                "sessionId INTEGER, " +
                "divisionId INTEGER, " +
                "teamId INTEGER PRIMARY KEY, "
                "teamNumber INTEGER, " +
                "teamName TEXT)"
            )
        except Exception:
            pass

        try:
            self.cur.execute(
                "CREATE TABLE CurrentTeamPlayer (" +
                "teamId INTEGER, " +
                "memberId INTEGER, " +
                "PRIMARY KEY (teamId, memberId))"
            )
        except Exception:
            pass
        
        try:
            self.cur.execute(
                "CREATE TABLE Player (" +
                "memberId INTEGER PRIMARY KEY, " +
                "playerName TEXT, " +
                "currentSkillLevel INTEGER)"
            )
        except Exception:
            pass
        
        gamePrefix = self.getGamePrefix(isEightBall)

        try:
            self.cur.execute(
                "CREATE TABLE {}BallTeamMatch (".format(gamePrefix) +
                "teamMatchId INTEGER PRIMARY KEY, datePlayed DATETIME, " +
                "sessionSeason TEXT CHECK(sessionSeason IN ('SPRING', 'SUMMER', 'FALL')), " + 
                "sessionYear INTEGER)"
            )
        except Exception:
            pass

        try:
            self.cur.execute(
                "CREATE TABLE {}BallPlayerMatch(".format(gamePrefix) +
                "playerMatchId INTEGER, teamMatchId INTEGER, team_name1 varchar(255), " +
                "player_name1 varchar(255), skill_level1 int, scoreId1 INTEGER, " + 
                "team_name2 varchar(255), player_name2 varchar(255), " +
                "skill_level2 INTEGER, scoreId2 INTEGER, PRIMARY KEY (playerMatchId, teamMatchId))"
            )
        except Exception:
            pass

        try:
            self.cur.execute(
                "CREATE TABLE {}BallDivision(divisionLink varchar(255) PRIMARY KEY)".format(gamePrefix)
            )
        except Exception:
            pass
        
        try:
            self.cur.execute(
                "CREATE TABLE {}BallScore(".format(gamePrefix) +
                "scoreId INTEGER PRIMARY KEY AUTOINCREMENT, match_pts_earned INTEGER, ball_pts_earned INTEGER, " +
                "ball_pts_needed INTEGER)"
            )
        except Exception:
            pass
        
        self.con.commit()

    def addDivisionValue(self, link, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)
        # Checks if value already exists in DB, and if not, adds it to DB
        if not self.isValueInDivisionTable(link, isEightBall):
            self.cur.execute("""INSERT INTO {}BallDivision VALUES ("{}")""".format(gamePrefix, link))
            self.con.commit()

    def isValueInDivisionTable(self, link, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)
        return self.cur.execute("SELECT COUNT(*) FROM {}BallDivision WHERE divisionLink='{}'".format(gamePrefix, link)).fetchone()[0] > 0

    def isValueInTeamMatchTable(self, teamMatchId, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)
        return self.cur.execute("SELECT COUNT(*) FROM {}BallTeamMatch WHERE teamMatchId = {}".format(gamePrefix, teamMatchId)).fetchone()[0] > 0

    def addTeamMatchValue(self, teamMatchId, apa_datetime, sessionSeason, sessionYear, isEightBall):
        try:
            gamePrefix = self.getGamePrefix(isEightBall)
            self.cur.execute("INSERT INTO {}BallTeamMatch VALUES ({}, '{}', '{}', {})".format(gamePrefix, teamMatchId, apa_datetime, sessionSeason, sessionYear))
            self.con.commit()
        except Exception:
            pass

    def countPlayerMatches(self, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)
        return self.cur.execute("SELECT COUNT(*) FROM {}BallPlayerMatch".format(gamePrefix)).fetchone()[0]
    
    def countTeamMatches(self, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)
        return self.cur.execute("SELECT COUNT(*) FROM {}BallTeamMatch".format(gamePrefix)).fetchone()[0]
    
    def addPlayerMatchValue(self, playerMatch, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)
        for playerResult in playerMatch.getPlayerMatchResult():
            self.cur.execute(self.formatScoreInsertQuery(playerResult.get_score(), isEightBall))

        scoreId = int(self.cur.execute("SELECT last_insert_rowid() FROM {}BallScore".format(gamePrefix)).fetchone()[0])
        
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
            f"""INSERT INTO {gamePrefix}BallPlayerMatch VALUES ({player_match_id}, {team_match_id}, "{team_name_1}", "{player_name1}", {skill_level1}, {score_id1}, "{team_name_2}", "{player_name2}", {skill_level2}, {score_id2})"""
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
        gamePrefix = self.getGamePrefix(isEightBall)
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
        gamePrefix = self.getGamePrefix(isEightBall)
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
        gamePrefix = self.getGamePrefix(isEightBall)
        return self.cur.execute(
            "SELECT n.playerMatchId, n.teamMatchId, n.player_name1, " +
            "n.team_name1, n.skill_level1, score1.match_pts_earned, score1.ball_pts_earned, score1.ball_pts_needed, " + 
            "n.player_name2, " +
            "n.team_name2, n.skill_level2, score2.match_pts_earned, score2.ball_pts_earned, score2.ball_pts_needed, t.datePlayed " + 
            "FROM {}BallPlayerMatch n ".format(gamePrefix) +
            "LEFT JOIN {}BallTeamMatch t ".format(gamePrefix) + 
            "ON n.teamMatchId = t.teamMatchId " +
            "LEFT JOIN {}BallScore score1 ".format(gamePrefix) +
            "ON score1.scoreId = n.scoreId1 " +
            "LEFT JOIN {}BallScore score2 ".format(gamePrefix) +
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