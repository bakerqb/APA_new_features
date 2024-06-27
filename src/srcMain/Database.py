import sqlite3
from tabulate import tabulate
from src.srcMain.Config import Config
from src.dataClasses.Team import Team
from utils.utils import *
from dataClasses.Game import Game

class Database:
    # ------------------------- Setup -------------------------
    def __init__(self):
        self.con = sqlite3.connect("results.db")
        self.cur = self.con.cursor()
        self.config = Config().getConfig()

    def refreshAllTables(self):
        self.dropTables()
        self.createTables()
    
    def dropTables(self):
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
            self.cur.execute("DROP TABLE PlayerMatch")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE Score")
        except Exception:
            pass

        try:
            self.cur.execute("DROP TABLE TeamMatch")
        except Exception:
            pass

        self.con.commit()

    def createTables(self):
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
                "PRIMARY KEY (divisionId))"
            )
        except Exception:
            pass

        try:
            self.cur.execute(
                "CREATE TABLE Team (" +
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

        try:
            self.cur.execute(
                "CREATE TABLE TeamMatch (" +
                "teamMatchId INTEGER PRIMARY KEY, " +
                "datePlayed DATETIME, " +
                "divisionId INTEGER)"
            )
        except Exception:
            pass

        try:
            self.cur.execute(
                "CREATE TABLE PlayerMatch(" +
                "playerMatchId INTEGER, teamMatchId INTEGER, teamId1 TEXT, " +
                "memberId1 INTEGER, skillLevel1 INTEGER, scoreId1 INTEGER, " + 
                "teamId2 TEXT, memberId2 INTEGER, skillLevel2 INTEGER, scoreId2 INTEGER, " +
                "PRIMARY KEY (playerMatchId, teamMatchId))"
            )
        except Exception:
            pass
        
        try:
            self.cur.execute(
                "CREATE TABLE Score(" +
                "scoreId INTEGER PRIMARY KEY AUTOINCREMENT, teamPtsEarned INTEGER, playerPtsEarned INTEGER, " +
                "playerPtsNeeded INTEGER)"
            )
        except Exception:
            pass
        
        self.con.commit()

    # ------------------------- Getting -------------------------
    def getTeamResults(self, teamId):
        return self.cur.execute(
            "SELECT s.sessionId, s.sessionSeason, s.sessionYear, d.divisionId, d.divisionName, d.dayOfWeek, d.game, " +
            "tm.teamMatchId, tm.datePlayed, pm.playerMatchId, t1.teamId, t1.teamNum, t1.teamName, " +
            "p1.memberId, p1.playerName, p1.currentSkillLevel, pm.skillLevel1, s1.teamPtsEarned, s1.playerPtsEarned, s1.playerPtsNeeded, " +
            "t2.teamId, t2.teamNum, t2.teamName, p2.memberId, p2.playerName, p2.currentSkillLevel, pm.skillLevel2, " +
            "s2.teamPtsEarned, s2.playerPtsEarned, s2.playerPtsNeeded " +
            "FROM Session s LEFT JOIN Division d ON s.sessionId = d.sessionId " +
            "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
            "LEFT JOIN Player p1 ON p1.memberId = pm.memberId1 " +
            "LEFT JOIN Player p2 ON p2.memberId = pm.memberId2 " +
            "LEFT JOIN Team t1 ON t1.teamId = pm.teamId1 " +
            "LEFT JOIN Team t2 ON t2.teamId = pm.teamId2 " +
            "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
            "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
            f"WHERE t1.teamId = {teamId} OR t2.teamId = {teamId} " +
            "ORDER BY tm.datePlayed"
        ).fetchall()

    def getLatestPlayerMatchesForPlayer(self, memberId, game, limit):
        return self.cur.execute(
            "SELECT s.sessionId, s.sessionSeason, s.sessionYear, d.divisionId, d.divisionName, d.dayOfWeek, d.game, " +
            "tm.teamMatchId, tm.datePlayed, pm.playerMatchId, t1.teamId, t1.teamNum, t1.teamName, " +
            "p1.memberId, p1.playerName, p1.currentSkillLevel, pm.skillLevel1, s1.teamPtsEarned, s1.playerPtsEarned, s1.playerPtsNeeded, " +
            "t2.teamId, t2.teamNum, t2.teamName, p2.memberId, p2.playerName, p2.currentSkillLevel, pm.skillLevel2, " +
            "s2.teamPtsEarned, s2.playerPtsEarned, s2.playerPtsNeeded " +
            "FROM Session s LEFT JOIN Division d ON s.sessionId = d.sessionId " +
            f"LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
            f"LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
            "LEFT JOIN Player p1 ON p1.memberId = pm.memberId1 " +
            "LEFT JOIN Player p2 ON p2.memberId = pm.memberId2 " +
            "LEFT JOIN Team t1 ON t1.teamId = pm.teamId1 " +
            "LEFT JOIN Team t2 ON t2.teamId = pm.teamId2 " +
            f"LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
            f"LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
            f"""WHERE d.game = "{game}" AND (p1.memberId = {memberId} OR p2.memberId = {memberId}) """ +
            f"ORDER BY tm.datePlayed DESC LIMIT {limit}"
            
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
    
    def getDatePlayed(self, teamMatchId: int):
        return self.cur.execute(
            f"SELECT datePlayed FROM TeamMatch WHERE teamMatchId = {teamMatchId}"
        ).fetchone()[0]

    def getTeamMatches(self, divisionId):
        return self.cur.execute(
            "SELECT tm.teamMatchId, d.divisionId " +
            "FROM Division d " +
            f"LEFT JOIN TeamMatch tm ON tm.divisionId = d.divisionId " +
            f"WHERE d.divisionId = {divisionId}"
        ).fetchall()
    
    def getTeamsFromDivision(self, divisionId):
        return self.cur.execute(f"SELECT * FROM Team WHERE divisionId = {divisionId}").fetchall()
    
    def getTeam(self, teamNum, divisionId):
        # Data comes in the format of list(divisionId, teamId, teamNum, teamName, memberId, playerName, currentSkillLevel)
        return self.cur.execute(
            "SELECT s.sessionId, s.sessionSeason, s.sessionYear, " +
            "d.divisionId, d.divisionName, d.dayOfWeek, d.game, " +
            "t.teamId, t.teamNum, t.teamName, p.memberId, p.playerName, p.currentSkillLevel " +
            "FROM Team t " +
            "LEFT JOIN Division d ON t.divisionId = d.divisionId " +
            "LEFT JOIN Session s ON d.sessionId = s.sessionId " +
            "LEFT JOIN CurrentTeamPlayer c ON c.teamId = t.teamId " +
            "LEFT JOIN Player p ON c.memberId = p.memberId " +
            f"WHERE t.teamNum={teamNum} AND t.divisionId={divisionId}"
        ).fetchall()
    
    def getTeamNum(self, teamId):
        return self.cur.execute(
            f"SELECT teamNum FROM Team WHERE teamId = {teamId}"
        ).fetchone()[0]
    
    def getDivisionIdFromTeamId(self, teamId):
        return self.cur.execute(
            f"SELECT divisionId FROM Team WHERE teamId = {teamId}"
        ).fetchone()[0]
    
    def getPlayerBasedOnTeamIdAndPlayerName(self, teamId, playerName):
        # Makes an assumption that no team will have two players with the exact same name
        return self.cur.execute(
            "SELECT p.memberId, p.playerName, p.currentSkillLevel " +
            "FROM currentTeamPlayer c LEFT JOIN Player p ON c.memberId = p.memberId " +
            f"""WHERE c.teamId = {teamId} AND p.playerName = "{playerName}" """
        ).fetchone()
    
    def getDivision(self, divisionId):
        self.createTables()
        division = self.cur.execute(
            "SELECT s.sessionId, s.sessionSeason, s.sessionYear, d.divisionId, d.divisionName, d.dayOfWeek, d.game " + 
            "FROM Division d LEFT JOIN Session s " +
            "ON d.sessionId = s.sessionId " +
            f"WHERE d.divisionId = {divisionId}"
        ).fetchall()
        if len(division) > 0:
            division = division[0]
        return division
    
    def getSession(self, sessionId):
        self.createTables()
        return self.cur.execute(f"SELECT * FROM Session WHERE sessionId = {sessionId}").fetchall()
    
    def getGame(self, divisionId):
        self.createTables()
        return self.cur.execute(f"SELECT game FROM Division WHERE divisionId = {divisionId}").fetchone()[0]
    

    # ------------------------- Inserting -------------------------
    def addPlayerMatch(self, playerMatch):
        for playerResult in playerMatch.getPlayerResults():
            score = playerResult.getScore()
            self.cur.execute(
                f"INSERT INTO Score VALUES (NULL, {score.getTeamPtsEarned()}, {score.getPlayerPtsEarned()}, {score.getPlayerPtsNeeded()})"
            )

        scoreId = int(self.cur.execute("SELECT last_insert_rowid() FROM Score").fetchone()[0])
        
        playerMatchId = playerMatch.getPlayerMatchId()
        teamMatchId = playerMatch.getTeamMatchId()
        teamId1 = playerMatch.getPlayerResults()[0].getTeam().getTeamId()
        memberId1 = playerMatch.getPlayerResults()[0].getPlayer().getMemberId()
        skillLevel1 = playerMatch.getPlayerResults()[0].getSkillLevel()
        scoreId1 = str(scoreId-1)
        teamId2 = playerMatch.getPlayerResults()[1].getTeam().getTeamId()
        memberId2 = playerMatch.getPlayerResults()[1].getPlayer().getMemberId()
        skillLevel2 = playerMatch.getPlayerResults()[1].getSkillLevel()
        scoreId2 = str(scoreId)


        self.cur.execute(
            f"""INSERT INTO PlayerMatch VALUES ({playerMatchId}, {teamMatchId}, {teamId1}, {memberId1}, {skillLevel1}, {scoreId1}, {teamId2}, {memberId2}, {skillLevel2}, {scoreId2})"""
        )
        self.con.commit()
    
    def addTeamMatch(self, teamMatchId, apaDatetime, divisionId):
        try:
            self.cur.execute(f"INSERT INTO TeamMatch VALUES ({teamMatchId}, '{apaDatetime}', {divisionId})")
            self.con.commit()
        except Exception:
            pass
    
    def addTeamInfo(self, team: Team):
        divisionId = team.getDivision().getDivisionId()
        teamId = team.getTeamId()
        teamNum = team.getTeamNum()
        teamName = team.getTeamName()
        self.addTeam(divisionId, teamId, teamNum, teamName)
        #TODO: Delete all currentTeamPlayer entries belonging to the team and re-add all the players
        # That way the table stays current
        
        for player in team.getPlayers():
            memberId = player.getMemberId()
            playerName = player.getPlayerName()
            currentSkillLevel = player.getCurrentSkillLevel()

            self.addCurrentTeamPlayer(teamId, memberId)
            self.addPlayer(memberId, playerName, currentSkillLevel)

    def addTeam(self, divisionId: int, teamId: int, teamNum: int, teamName: str):
        self.createTables()
        try:
            self.cur.execute(
                f"""INSERT INTO Team VALUES ({divisionId}, {teamId}, {teamNum}, "{teamName}")"""
            )
        except Exception:
            pass

        self.con.commit()

    def addCurrentTeamPlayer(self, teamId: int, memberId: int):
        self.createTables()
        try:
            self.cur.execute(
                f"INSERT INTO CurrentTeamPlayer VALUES ({teamId}, {memberId})"
            )
        except Exception:
            pass
        self.con.commit()

    def addPlayer(self, memberId: int, playerName: str, currentSkillLevel: int):
        self.createTables()
        try:
            self.cur.execute(
                f"""INSERT INTO Player VALUES ({memberId}, "{playerName}", {currentSkillLevel})"""
            )
        except Exception:
            pass
        self.con.commit() 

    def addSession(self, session):
        self.createTables()
        
        if not self.getSession(session.getSessionId()):
            self.cur.execute(f"INSERT INTO Session VALUES ({session.getSessionId()}, '{session.getSessionSeason()}', {session.getSessionYear()})")
            self.con.commit()
    
    def addDivision(self, division):
        self.createTables()
        session = division.getSession()
        self.addSession(session)

        if not self.getDivision(division.getDivisionId()):
            self.cur.execute(
                "INSERT INTO Division VALUES (" +
                f"{session.getSessionId()}, " +
                f"{division.getDivisionId()}, " +
                f"'{division.getDivisionName()}', " + 
                f"{division.getDayOfWeek()}, " +
                f"'{division.getGame()}')"
            )
            self.con.commit()  


    # ------------------------- Deleting -------------------------
    def deleteSession(self, sessionId):
        self.deleteDivision(sessionId, None)
        
        self.cur.execute(f"DELETE FROM Session WHERE sessionId = {sessionId}")
        self.con.commit()

    def deleteDivision(self, sessionId, divisionId):
        self.deleteTeam(sessionId, divisionId)
        self.deleteTeamMatch(sessionId, divisionId)

        if divisionId is None:
            self.cur.execute(f"DELETE FROM Division WHERE sessionId = {sessionId}")
        else:
            self.cur.execute(f"DELETE FROM Division WHERE divisionId = {divisionId}")
    
        self.con.commit()

    def deleteTeamMatch(self, sessionId, divisionId):
        self.deletePlayerMatch(sessionId, divisionId)

        if divisionId is None:
            self.cur.execute(
                "DELETE FROM TeamMatch WHERE divisionId IN (" +
                    "SELECT divisionId FROM Division d " +
                    "LEFT JOIN Session s ON s.sessionId = d.sessionId " +
                    f"WHERE s.sessionId = {sessionId}" +
                ")"
            )
        else:
            self.cur.execute(
                f"DELETE FROM TeamMatch WHERE divisionId = {divisionId}"
            )
            
        self.con.commit()
    
    def deletePlayerMatch(self, sessionId, divisionId):
        self.deleteScore(sessionId, divisionId)

        if divisionId is None:
            self.cur.execute(
                "DELETE FROM PlayerMatch WHERE teamMatchId IN (" +
                    "SELECT tm.teamMatchId FROM TeamMatch tm" +
                    "LEFT JOIN Division d ON tm.divisionId = d.divisionId " +
                    "LEFT JOIN Session s ON d.sessionId = s.sessionId " +
                    f"WHERE sessionId = {sessionId}" +
                ")"
            )
        else:
            self.cur.execute(
                "DELETE FROM PlayerMatch WHERE teamMatchId IN (" +
                    f"SELECT teamMatchId FROM TeamMatch WHERE divisionId = {divisionId}" +
                ")"
            )
        self.con.commit()
    
    def deleteScore(self, sessionId, divisionId):
        for i in range(2):
            if divisionId is None:
                self.cur.execute(
                    f"DELETE FROM Score WHERE scoreId IN (" +
                        f"SELECT pm.scoreId{str(i+1)} FROM PlayerMatch pm " +
                        f"LEFT JOIN TeamMatch tm ON pm.teamMatchId = tm.teamMatchId " +
                        "LEFT JOIN Division d ON tm.divisionId = d.divisionId " +
                        "LEFT JOIN Session s ON d.sessionId = s.sessionId "
                        f"WHERE s.sessionId = {sessionId}" +
                    ")"
                )
            else:
                self.cur.execute(
                    f"DELETE FROM Score WHERE scoreId IN (" +
                        f"SELECT pm.scoreId{str(i+1)} FROM PlayerMatch pm " +
                        f"LEFT JOIN TeamMatch tm ON pm.teamMatchId = tm.teamMatchId " +
                        f"WHERE tm.divisionId = {divisionId}" +
                    ")"
                )
        self.con.commit()
    
    def deleteTeam(self, sessionId, divisionId):
        self.deleteCurrentTeamPlayer(sessionId, divisionId)
        
        if divisionId is None:
            self.cur.execute(
                "DELETE FROM Team WHERE divisionId IN (" +
                    "SELECT d.divisionId FROM Division d " +
                    "LEFT JOIN Session s ON d.sessionId = s.sessionId " +
                    f"WHERE sessionId = {sessionId}" +
                ")"
            )
        else:
            self.cur.execute(f"DELETE FROM Team WHERE divisionId = {divisionId}")
        self.con.commit()
        
    def deleteCurrentTeamPlayer(self, sessionId, divisionId):
        if divisionId is None:
            self.cur.execute(
                "DELETE FROM CurrentTeamPlayer WHERE teamId IN (" +
                    "SELECT t.teamId FROM Team t " +
                    "LEFT JOIN Division d ON t.divisionId = d.divisionId " +
                    "LEFT JOIN Session s ON d.sessionId = d.divisionId " +
                    f"WHERE sessionId = {sessionId}"
                ")"
            )
        else:
            self.cur.execute(
                "DELETE FROM CurrentTeamPlayer WHERE teamId IN (" +
                    f"SELECT teamId FROM Team WHERE divisionId = {divisionId}"
                ")"
            )
        self.con.commit()
    
    # ------------------------- Checking -------------------------
    def isValueInTeamMatchTable(self, teamMatchId):
        return self.cur.execute(f"SELECT COUNT(*) FROM TeamMatch WHERE teamMatchId = {teamMatchId}").fetchone()[0] > 0

    # ------------------------- Counting -------------------------
    def countPlayerMatches(self):
        return self.cur.execute("SELECT COUNT(*) FROM PlayerMatch").fetchone()[0]

    
    # ------------------------- Skill Level -------------------------
    def createSkillLevelMatrix(self, game):
        matrix = []
        matrix.append([])
        
        numSkillLevels = 0
        if game == Game.EightBall.value:
            numSkillLevels = EIGHT_BALL_NUM_SKILL_LEVELS
        elif game == Game.NineBall.value:
            numSkillLevels = NINE_BALL_NUM_SKILL_LEVELS
        
        for i in range(0, numSkillLevels + 1):
            matrix[0].append(i)
        for i in range(1, numSkillLevels + 1):
            matrix.append([i] + [0] * numSkillLevels)
        for i in range(1, numSkillLevels + 1):
            for j in range(i+1, numSkillLevels + 1):
                matchesLowAgainstHigh = self.cur.execute(
                    "SELECT SUM(s1.teamPtsEarned), SUM(s2.teamPtsEarned), COUNT(*) " + 
                    "FROM Division d " +
                    "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                    "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                    "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                    "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                    f"WHERE pm.skillLevel1 = {i} AND pm.skillLevel2 = {j} AND d.game = '{game}'"
                ).fetchone()

                matchesHighAgainstLow = self.cur.execute(
                    "SELECT SUM(s1.teamPtsEarned), SUM(s2.teamPtsEarned), COUNT(*) " + 
                    "FROM Division d " +
                    "LEFT JOIN TeamMatch tm ON d.divisionId = tm.divisionId " +
                    "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
                    "LEFT JOIN Score s1 ON s1.scoreId = pm.scoreId1 " +
                    "LEFT JOIN Score s2 ON s2.scoreId = pm.scoreId2 " +
                    f"WHERE pm.skillLevel1 = {j} AND pm.skillLevel2 = {i} AND d.game = '{game}'"
                ).fetchone()

                games = matchesLowAgainstHigh[2] + matchesHighAgainstLow[2]
                if games > 0:
                    ptsFromLowerRatedPlayer = (matchesLowAgainstHigh[0] if matchesLowAgainstHigh[0] else 0)  + (matchesHighAgainstLow[1] if matchesHighAgainstLow[1] else 0)
                    ptsFromHigherRatedPlayer = (matchesLowAgainstHigh[1] if matchesLowAgainstHigh[1] else 0) + (matchesHighAgainstLow[0] if matchesHighAgainstLow[0] else 0)
                    matrix[i][j] = str(round(ptsFromLowerRatedPlayer/games, 1)) + " pts expected\n" + str(games) + " games"
                    matrix[j][i] = str(round(ptsFromHigherRatedPlayer/games, 1)) + " pts expected\n" + str(games) + " games"
        
        print(tabulate(matrix, headers="firstrow", tablefmt="fancy_grid"))
