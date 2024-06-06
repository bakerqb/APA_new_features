import sqlite3
from tabulate import tabulate
from src.srcMain.Config import Config
from src.dataClasses.Team import Team
import statistics

class Database:
    ############### Helper functions ###############
    def __init__(self):
        self.con = sqlite3.connect("results.db")
        self.cur = self.con.cursor()
        self.config = Config().getConfig()

    
    def getGamePrefix(self, isEightBall):
        return 'Eight' if isEightBall else 'Nine'
    
    def getMedian(self, scores):
        nums = []
        for item in scores:
            nums.append(item[0])
        return statistics.median(nums)
    
    ############### Game agnostic functions ###############

    def getTeamsFromDivision(self, sessionId, divisionId):
        return self.cur.execute(f"SELECT * FROM Team WHERE sessionId = {sessionId} AND divisionId = {divisionId}").fetchall()

    def getLastScoreId(self, is_eight_ball):
        gamePrefix = self.getGamePrefix(is_eight_ball)
        
    
    def getTeam(self, teamName, teamNum, divisionId, sessionId):
        # Data comes in the format of list(divisionId, teamId, teamNum, teamName, memberId, playerName, currentSkillLevel)
        return self.cur.execute(
            "SELECT s.sessionId, s.sessionSeason, s.sessionYear, " +
            "d.divisionId, d.divisionName, d.dayOfWeek, d.game, " +
            "t.teamId, t.teamNum, t.teamName, p.memberId, p.playerName, p.currentSkillLevel " +
            "FROM Team t " +
            "LEFT JOIN Division d ON t.divisionId = d.divisionId AND t.sessionId = d.sessionId " +
            "LEFT JOIN Session s ON d.sessionId = s.sessionId " +
            "LEFT JOIN CurrentTeamPlayer c ON c.teamId = t.teamId " +
            "LEFT JOIN Player p ON c.memberId = p.memberId " +
            f"""WHERE t.teamName="{teamName}" AND t.teamNum={teamNum} AND t.divisionId={divisionId} AND t.sessionId={sessionId}"""
        ).fetchall()
    
    def getPlayerBasedOnTeamIdAndPlayerName(self, teamId, playerName):
        # Makes an assumption that no team will have two players with the exact same name
        return self.cur.execute(
            "SELECT p.memberId, p.playerName, p.currentSkillLevel " +
            "FROM currentTeamPlayer c LEFT JOIN Player p ON c.memberId = p.memberId " +
            f"""WHERE c.teamId = {teamId} AND p.playerName = "{playerName}" """
        ).fetchone()
    
    def addTeamInfo(self, team: Team):
        teamData = team.toJson()
        sessionId = teamData.get('division').get('session').get('sessionId')
        divisionId = teamData.get('division').get('divisionId')
        teamId = teamData.get('teamId')
        teamNum = teamData.get('teamNum')
        teamName = teamData.get('teamName')
        self.addTeam(sessionId, divisionId, teamId, teamNum, teamName)
        #TODO: Delete all currentTeamPlayer entries belonging to the team and re-add all the players
        # That way the table stays current
        
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
        division = self.cur.execute(
            "SELECT s.sessionId, s.sessionSeason, s.sessionYear, d.divisionId, d.divisionName, d.dayOfWeek, d.game " + 
            "FROM Division d LEFT JOIN Session s " +
            "ON d.divisionId = s.sessionId " +
            "WHERE d.divisionId = {}".format(divisionId)
        ).fetchall()
        if len(division) > 0:
            division = division[0]
        return division
    
    def getSession(self, sessionId):
        self.createTables(True)
        return self.cur.execute("SELECT * FROM Session WHERE sessionId = {}".format(sessionId)).fetchall()
        

    def addSession(self, session):
        self.createTables(True)
        
        if not self.getSession(session.get('sessionId')):
            self.cur.execute(f"INSERT INTO Session VALUES ({session.get('sessionId')}, '{session.get('sessionSeason')}', {session.get('sessionYear')})")
            self.con.commit()
    
    def addDivision(self, division):
        self.createTables(True)
        divisionData = division.toJson()
        session = divisionData.get('session')
        self.addSession(session)

        if not self.getDivision(divisionData.get('divisionId')):
            self.cur.execute(
                "INSERT INTO Division VALUES (" +
                f"{session.get('sessionId')}, " +
                f"{divisionData.get('divisionId')}, " +
                f"'{divisionData.get('divisionName')}', " + 
                f"{divisionData.get('dayOfWeek')}, " +
                f"'{divisionData.get('game')}')"
            )
            self.con.commit()

    def deleteSession(self, sessionId):
        divisionIds = list(map(lambda divisionId: divisionId[0], self.cur.execute(f"SELECT divisionId from Division WHERE sessionId = {sessionId}").fetchall()))
        for divisionId in divisionIds:
            self.deleteDivision(divisionId)
        
        self.cur.execute(f"DELETE FROM Session WHERE sessionId = {sessionId}")
        self.con.commit()

    def deleteDivision(self, divisionId):
        teamIds = list(map(lambda divisionId: divisionId[0], self.cur.execute(f"SELECT teamId from Team WHERE divisionId = {divisionId}").fetchall()))
        for teamId in teamIds:
            self.deleteTeam(teamId)
        self.cur.execute(f"DELETE FROM Division WHERE divisionId  = {divisionId}")
        self.con.commit()

    def deleteTeam(self, teamId):
        
        #TODO: find a way to connect EightBall and NineBall related tables to divisionId, and then delete those tables
        
        game = self.cur.execute(f"SELECT game FROM Division d LEFT JOIN Team t ON d.divisionId = t.divisionId WHERE t.teamId = {teamId}").fetchone()[0]
        gamePrefix = self.getGamePrefix(game)
        # self.cur.execute(f"DELETE FROM {gamePrefix}BallPlayerMatch AS p WHERE p.teamMatchId IN (SELECT t.teamMatchId FROM {gamePrefix}BallTeamMatch AS t WHERE t.sessionSeason = '{sessionSeason}' AND t.sessionYear = {})".format(gamePrefix, gamePrefix, sessionSeason, str(sessionYear)))




        self.cur.execute(f"DELETE FROM Team WHERE teamId  = {teamId}")
        self.cur.execute(f"DELETE FROM CurrentTeamPlayer WHERE teamId = {teamId}")
        self.con.commit()
        
    
    def deleteSessionData(self):
        sessionSeason = self.config.get('session_season_in_question')
        sessionYear = self.config.get('session_year_in_question')
        game = self.config.get('game')
        gamePrefix = self.getGamePrefix(game == '8-ball')

        # TODO: fix these queries
        self.cur.execute("DELETE FROM {}BallPlayerMatch AS p WHERE p.teamMatchId IN (SELECT t.teamMatchId FROM {}BallTeamMatch AS t WHERE t.sessionSeason = '{}' AND t.sessionYear = {})".format(gamePrefix, gamePrefix, sessionSeason, str(sessionYear)))
        self.cur.execute("DELETE FROM {}BallTeamMatch WHERE sessionSeason = '{}' AND sessionYear = {}".format(gamePrefix, sessionSeason, str(sessionYear)))
        self.con.commit()
    
    def refreshAllTables(self, isEightBall):
        self.dropTables(isEightBall)
        self.createTables(isEightBall)
    
    def dropTables(self, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)

        try:
            self.cur.execute("DROP TABLE Session")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE Division")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE Team")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE CurrentTeamPlayer")
        except Exception:
            pass
        
        try:
            self.cur.execute("DROP TABLE Player")
        except Exception:
            pass

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
                "teamNum INTEGER, " +
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
                "divisionId INTEGER, sessionId INTEGER)"
            )
        except Exception:
            pass

        try:
            self.cur.execute(
                "CREATE TABLE {}BallPlayerMatch(".format(gamePrefix) +
                "playerMatchId INTEGER, teamMatchId INTEGER, teamId1 TEXT, " +
                "memberId1 INTEGER, skillLevel1 INTEGER, scoreId1 INTEGER, " + 
                "teamId2 TEXT, memberId2 INTEGER, skillLevel2 INTEGER, scoreId2 INTEGER, " +
                "PRIMARY KEY (playerMatchId, teamMatchId))"
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
                "scoreId INTEGER PRIMARY KEY AUTOINCREMENT, matchPtsEarned INTEGER, ballPtsEarned INTEGER, " +
                "ballPtsNeeded INTEGER)"
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

    def addTeamMatchValue(self, teamMatchId, apa_datetime, divisionId, sessionId, isEightBall):
        try:
            gamePrefix = self.getGamePrefix(isEightBall)
            self.cur.execute("INSERT INTO {}BallTeamMatch VALUES ({}, '{}', {}, {})".format(gamePrefix, teamMatchId, apa_datetime, divisionId, sessionId))
            self.con.commit()
        except Exception:
            pass

    def countPlayerMatches(self, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)
        return self.cur.execute("SELECT COUNT(*) FROM {}BallPlayerMatch".format(gamePrefix)).fetchone()[0]
    
    def countTeamMatches(self, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)
        return self.cur.execute("SELECT COUNT(*) FROM {}BallTeamMatch".format(gamePrefix)).fetchone()[0]
    
    def addPlayerMatch(self, playerMatch, isEightBall):
        gamePrefix = self.getGamePrefix(isEightBall)
        playerMatch = playerMatch.toJson()
        for playerResult in playerMatch.get('playerResults'):
            self.cur.execute(self.formatScoreInsertQuery(playerResult.get('score'), isEightBall))

        scoreId = int(self.cur.execute("SELECT last_insert_rowid() FROM {}BallScore".format(gamePrefix)).fetchone()[0])
        
        player_match_id = playerMatch.get('playerMatchId')
        team_match_id = playerMatch.get('teamMatchId')
        teamId1 = playerMatch.get('playerResults')[0].get('team').get('teamId')
        memberId1 = playerMatch.get('playerResults')[0].get('player').get('memberId')
        skillLevel1 = playerMatch.get('playerResults')[0].get('skill_level')
        scoreId1 = str(scoreId-1)
        teamId2 = playerMatch.get('playerResults')[1].get('team').get('teamId')
        memberId2 = playerMatch.get('playerResults')[1].get('player').get('memberId')
        skillLevel2 = playerMatch.get('playerResults')[1].get('skill_level')
        scoreId2 = str(scoreId)


        self.cur.execute(
            f"""INSERT INTO {gamePrefix}BallPlayerMatch VALUES ({player_match_id}, {team_match_id}, {teamId1}, {memberId1}, {skillLevel1}, {scoreId1}, {teamId2}, {memberId2}, {skillLevel2}, {scoreId2})"""
        )
        self.con.commit()

    def formatScoreInsertQuery(self, score, isEightBall):
        if isEightBall:
            return "INSERT INTO EightBallScore VALUES ({}, {}, {}, {})".format(
                "NULL", 
                str(score.get('match_pts_earned')), 
                str(score.get('games_won')), 
                str(score.get('games_needed'))
            )
        else:
            return "INSERT INTO NineBallScore VALUES ({}, {}, {}, {})".format(
                "NULL", 
                str(score.get('match_pts_earned')), 
                str(score.get('ball_pts_earned')), 
                str(score.get('ball_pts_needed'))
            )
    
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
        # TODO: Review this function
        
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
    
    def getTeamResults(self, teamId):
        # TODO: find game based off of just teamId :) so you only have to pass in teamId for these parameters
        game = self.cur.execute(f"SELECT d.game FROM Division d, Team t WHERE t.divisionId = d.divisionId AND t.teamId = {teamId}").fetchone()[0]
        gamePrefix = self.getGamePrefix(game == '8-ball')
        return self.cur.execute(
            "SELECT s.sessionId, s.sessionSeason, s.sessionYear, d.divisionId, d.divisionName, d.dayOfWeek, d.game, " +
            "tm.teamMatchId, tm.datePlayed, pm.playerMatchId, pr1.teamId, pr1.teamNum, pr1.teamName, " +
            "pr1.memberId, pr1.playerName, pr1.currentSkillLevel, pm.skillLevel1, pr1.matchPtsEarned, pr1.ballPtsEarned, pr1.ballPtsNeeded, " +
            "pr2.teamId, pr2.teamNum, pr2.teamName, pr2.memberId, pr2.playerName, pr2.currentSkillLevel, pm.skillLevel2, " +
            "pr2.matchPtsEarned, pr2.ballPtsEarned, pr2.ballPtsNeeded " +
            "FROM Session s LEFT JOIN Division d ON s.sessionId = d.sessionId " +
            f"LEFT JOIN {gamePrefix}BallTeamMatch tm ON d.divisionId = tm.divisionId AND s.sessionId = tm.sessionId " +
            f"LEFT JOIN {gamePrefix}BallPlayerMatch pm ON pm.teamMatchId = tm.teamMatchId "
            "LEFT JOIN (SELECT t.teamId, t.teamNum, t.teamName, p.memberId, p.playerName, p.currentSkillLevel, " +
                    "s.scoreId, s.matchPtsEarned, s.ballPtsEarned, s.ballPtsNeeded " +
                    f"FROM Team t, Player p, {gamePrefix}BallScore s) pr1 " +
            "ON pr1.teamId = pm.teamId1 AND pr1.memberId = pm.memberId1 AND pr1.scoreId = pm.scoreId1 " +
            "LEFT JOIN (SELECT t.teamId, t.teamNum, t.teamName, p.memberId, p.playerName, p.currentSkillLevel, " +
                    "s.scoreId, s.matchPtsEarned, s.ballPtsEarned, s.ballPtsNeeded " +
                    f"FROM Team t, Player p, {gamePrefix}BallScore s) pr2 " +
            "ON pr2.teamId = pm.teamId2 AND pr2.memberId = pm.memberId2 AND pr2.scoreId = pm.scoreId2 " +
            f"WHERE pr1.teamId = {teamId} OR pr2.teamId = {teamId} " +
            "ORDER BY tm.datePlayed"
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
    
    def getTeamRoster(self, teamId):
        return self.cur.execute(
            "SELECT p.memberId, p.playerName, p.currentSkillLevel " +
            "FROM Player p LEFT JOIN CurrentTeamPlayer c ON p.memberId = c.memberId " +
            "LEFT JOIN Team t ON t.teamId = c.teamId " +
            f"WHERE t.teamId = {teamId}"
        ).fetchall()
    
    def getDivisions(self, sessionId):
        return self.cur.execute(
            f"SELECT s.sessionId, s.sessionSeason, s.sessionYear, d.divisionId, d.divisionName, d.dayOfWeek, d.game " +
            "FROM Session s LEFT JOIN Division d ON s.sessionId = d.sessionId " +
            f"WHERE s.sessionId = {sessionId}"
        ).fetchall()
    
    def getSessions(self):
        return self.cur.execute("SELECT * FROM Session s").fetchall()



    ############### 8 Ball functions ###############

    def deleteEightBallTeamMatch(self, teamMatchId):
        self.cur.execute("DELETE FROM EightBallTeamMatch WHERE teamMatchId = {}".format(teamMatchId))
        self.con.commit()
    
    
    def getEightBallDivisionLinks(self):
        return self.cur.execute("SELECT * FROM EightBallDivision").fetchall()