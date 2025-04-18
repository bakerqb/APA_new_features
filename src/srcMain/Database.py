import sqlite3
from tabulate import tabulate
from dataClasses.Team import Team
from dataClasses.Division import Division
from utils.utils import *
from dataClasses.Format import Format
from dataClasses.SearchCriteria import SearchCriteria
from dataClasses.PlayerMatch import PlayerMatch
from dataClasses.Session import Session
from typing import Tuple
from srcMain.Typechecked import Typechecked
from src.srcMain.DatabaseTypes import DatabaseTypes

class Database(Typechecked):
    # ------------------------- Setup -------------------------
    def __init__(self):
        self.con = sqlite3.connect("apa_data.db", check_same_thread=False)
        self.cur = self.con.cursor()

    def refreshAllTables(self) -> None:
        self.dropTables()
        self.createTables()
    
    def dropTables(self) -> None:
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

    def createTables(self) -> None:
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
                "CREATE TABLE TempTeamMatch (" +
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
                "memberId1 INTEGER, skillLevel1 INTEGER, adjustedSkillLevel1 INTEGER, scoreId1 INTEGER, " + 
                "teamId2 TEXT, memberId2 INTEGER, skillLevel2 INTEGER, adjustedSkillLevel2 INTEGER, scoreId2 INTEGER, " +
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
    def getPlayerMatches(self, sessionId: int | None, divisionId: int | None, teamId: int | None,
                         memberId: int | None, format: Format, limit: int | None, datePlayed: str | None,
                         playerMatchId: int | None, adjustedSkillLevel1range: Tuple[int] | None,
                         adjustedSkillLevel2range: Tuple[int] | None) -> List[DatabaseTypes.PlayerMatch]:
        return self.cur.execute(
            "SELECT s.sessionId, s.sessionSeason, s.sessionYear, d.divisionId, d.divisionName, d.dayOfWeek, d.game, " +
            "tm.teamMatchId, tm.datePlayed, pm.playerMatchId, t1.teamId, t1.teamNum, t1.teamName, " +
            "p1.memberId, p1.playerName, p1.currentSkillLevel, pm.skillLevel1, pm.adjustedSkillLevel1, s1.teamPtsEarned, s1.playerPtsEarned, s1.playerPtsNeeded, " +
            "t2.teamId, t2.teamNum, t2.teamName, p2.memberId, p2.playerName, p2.currentSkillLevel, pm.skillLevel2, pm.adjustedSkillLevel2, " +
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
            "WHERE pm.playerMatchId IS NOT NULL " +
            (f"AND s.sessionId = {sessionId} " if sessionId is not None else "") +
            (f"AND d.divisionId = {divisionId} " if divisionId is not None else "") +
            (f"AND t1.teamId = {teamId} OR t2.teamId = {teamId} " if teamId is not None else "") +
            (f"""AND d.game = "{format.value}" """ if format is not None else "") +
            (f"AND (p1.memberId = {memberId} OR p2.memberId = {memberId}) " if memberId is not None else "") +
            (f"""AND (tm.datePlayed < "{datePlayed}") """ if datePlayed is not None else "") +
            (f"AND (pm.playerMatchId >= {playerMatchId}) " if playerMatchId is not None else "") +
            (f"AND (pm.adjustedSkillLevel1 >= {adjustedSkillLevel1range[0]} AND pm.adjustedSkillLevel1 < {adjustedSkillLevel1range[1]}) " if adjustedSkillLevel1range is not None else "") +
            (f"AND (pm.adjustedSkillLevel2 >= {adjustedSkillLevel2range[0]} AND pm.adjustedSkillLevel2 < {adjustedSkillLevel2range[1]}) " if adjustedSkillLevel2range is not None else "") +
            "ORDER BY tm.datePlayed DESC " +
            (f"LIMIT {limit}" if limit is not None else "")
        ).fetchall()
    
    def getTeamRoster(self, teamId: int) -> List[DatabaseTypes.Player]:
        return self.cur.execute(
            "SELECT p.memberId, p.playerName, p.currentSkillLevel " +
            "FROM Player p LEFT JOIN CurrentTeamPlayer c ON p.memberId = c.memberId " +
            "LEFT JOIN Team t ON t.teamId = c.teamId " +
            f"WHERE t.teamId = {teamId}"
        ).fetchall()
    
    def getDivisions(self, sessionId: int) -> List[DatabaseTypes.Division]:
        return self.cur.execute(
            f"SELECT s.sessionId, s.sessionSeason, s.sessionYear, d.divisionId, d.divisionName, d.dayOfWeek, d.game " +
            "FROM Session s LEFT JOIN Division d ON s.sessionId = d.sessionId " +
            f"WHERE s.sessionId = {sessionId} ORDER BY d.dayOfWeek"
        ).fetchall()
    
    def getSessions(self) -> List[DatabaseTypes.Session]:
        return self.cur.execute("SELECT * FROM Session s ORDER BY sessionId DESC").fetchall()
    
    def getDatePlayed(self, teamMatchId: int) -> str:
        return self.cur.execute(
            f"SELECT datePlayed FROM TempTeamMatch WHERE teamMatchId = {teamMatchId}"
        ).fetchone()[0]

    def getTeamMatches(self, divisionId: int) -> List[DatabaseTypes.TeamMatch]:
        return self.cur.execute(
            "SELECT tm.teamMatchId, d.divisionId " +
            "FROM Division d " +
            f"LEFT JOIN TeamMatch tm ON tm.divisionId = d.divisionId " +
            f"WHERE d.divisionId = {divisionId} AND " +
            f"tm.teamMatchId NOT IN (" +
                "SELECT pm.teamMatchId FROM PlayerMatch pm " +
                "LEFT JOIN TeamMatch tm " +
                "ON pm.teamMatchId = tm.teamMatchId " +
                f"WHERE tm.divisionId = {divisionId}" +
            ") AND tm.teamMatchId IS NOT NULL"
        ).fetchall()
    
    def getUnscrapedTempTeamMatches(self, divisionId: int, teamMatchId: int | None) -> List[DatabaseTypes.TeamMatch]:
        return self.cur.execute(
            "SELECT ttm.teamMatchId, d.divisionId, ttm.datePlayed " +
            "FROM Division d " +
            f"LEFT JOIN TempTeamMatch ttm ON ttm.divisionId = d.divisionId " +
            f"WHERE d.divisionId = {divisionId} " +
            f"AND ttm.teamMatchId NOT IN (SELECT teamMatchId FROM TeamMatch WHERE divisionId = {divisionId}) " +
            ("" if teamMatchId is None else f"AND teamMatchId = {teamMatchId}")
        ).fetchall()
    
    def getTeamsFromDivision(self, divisionId: int) -> List[DatabaseTypes.TeamWithoutRoster]:
        return self.cur.execute(f"SELECT * FROM Team WHERE divisionId = {divisionId}").fetchall()
    
    def getTeam(self, teamNum: int | None, divisionId: int | None, teamId: int | None) -> DatabaseTypes.TeamWithRoster:
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
            "WHERE t.teamId IS NOT NULL " + 
            (f"AND t.teamNum = {teamNum} " if teamNum is not None else "") +
            (f"AND t.divisionId = {divisionId} " if divisionId is not None else "") +
            (f"AND t.teamId = {teamId} " if teamId is not None else "")
        ).fetchall()
    
    def getTeamNum(self, teamId: int) -> int:
        return self.cur.execute(
            f"SELECT teamNum FROM Team WHERE teamId = {teamId}"
        ).fetchone()[0]
    
    def getDivisionIdFromTeamId(self, teamId: int) -> int:
        return self.cur.execute(
            f"SELECT divisionId FROM Team WHERE teamId = {teamId}"
        ).fetchone()[0]
    
    def getPlayer(self, teamId: int | None, playerName: str | None, memberId: int | None) -> DatabaseTypes.Player:
        # Makes an assumption that no team will have two players with the exact same name
        return self.cur.execute(
            "SELECT p.memberId, p.playerName, p.currentSkillLevel " +
            "FROM currentTeamPlayer c LEFT JOIN Player p ON c.memberId = p.memberId " +
            "WHERE p.memberId IS NOT NULL " +
            (f"AND c.teamId = {teamId} " if teamId is not None else "") +
            (f"""AND p.playerName = "{playerName}" """ if playerName is not None else "") +
            (f"AND p.memberId = {memberId} " if memberId is not None else "")
        ).fetchone()
    
    def getDivision(self, divisionId: int) -> DatabaseTypes.Division:
        self.createTables()
        division = self.cur.execute(
            "SELECT s.sessionId, s.sessionSeason, s.sessionYear, d.divisionId, d.divisionName, d.dayOfWeek, d.game " + 
            "FROM Division d LEFT JOIN Session s " +
            "ON d.sessionId = s.sessionId " +
            f"WHERE d.divisionId = {divisionId}"
        ).fetchone()
        return division
    
    def getSession(self, sessionId: int) -> DatabaseTypes.Session:
        if sessionId is None:
            return None
        self.createTables()
        return self.cur.execute(f"SELECT * FROM Session WHERE sessionId = {sessionId}").fetchone()
    
    def getMostRecentSessionId(self, format: Format) -> int:
        self.createTables()
        sqlRows = self.getPlayerMatches(None, None, None, None, format, None, None, None, None, None)
        if len(sqlRows) == 0:
            return None
        return sqlRows[0][0]
    
    def getFormat(self, divisionId: int) -> Format:
        self.createTables()
        return Format(self.cur.execute(f"SELECT game FROM Division WHERE divisionId = {divisionId}").fetchone()[0])
    
    def getPlayers(self, searchCriteria: SearchCriteria) -> List[DatabaseTypes.PlayerWithDateLastPlayed]:
        self.createTables()
        return self.cur.execute(
            "SELECT pInfo.memberId, pInfo.playerName, pInfo.currentSkillLevel, pInfo.datePlayed FROM (" +
                "SELECT players.memberId, " +
                "players.playerName, " +
                "players.currentSkillLevel, " +
                "players.datePlayed, " +
                "ROW_NUMBER() OVER (PARTITION BY players.memberId ORDER BY players.datePlayed DESC) AS row_number " +
                "FROM (" +
                    "SELECT p1.memberId, p1.playerName, p1.currentSkillLevel, tm1.datePlayed " +
                    "FROM Player p1 " +
                    "LEFT JOIN PlayerMatch pm1 ON p1.memberId = pm1.memberId1 " +
                    "LEFT JOIN TeamMatch tm1 ON pm1.teamMatchId = tm1.teamMatchId " +
                    "UNION " +
                    "SELECT p2.memberId, p2.playerName, p2.currentSkillLevel, tm2.datePlayed " +
                    "FROM Player p2 " +
                    "LEFT JOIN PlayerMatch pm2 ON p2.memberId = pm2.memberId2 " +
                    "LEFT JOIN TeamMatch tm2 ON pm2.teamMatchId = tm2.teamMatchId" +
                ") players " +
            ") pInfo WHERE row_number = 1 " +
            ("" if not searchCriteria.getMemberId() else f"AND memberId = {searchCriteria.getMemberId()} ") +
            ("" if not searchCriteria.getPlayerName() else f"AND playerName LIKE '%{searchCriteria.getPlayerName()}%' ") +
            ("" if not searchCriteria.getMinSkillLevel() else f"AND currentSkillLevel >= {searchCriteria.getMinSkillLevel()} ") +
            ("" if not searchCriteria.getMaxSkillLevel() else f"AND currentSkillLevel <= {searchCriteria.getMaxSkillLevel()} ") +
            ("" if not searchCriteria.getDateLastPlayed() else f"AND CAST(datePlayed AS DATE) >= CAST({searchCriteria.getDateLastPlayed()} AS DATE)") +
            "ORDER BY datePlayed DESC, playerName ASC"
            
        ).fetchall()
    
    def getLastSessionIdPlayedByPlayer(self, memberId: int) -> int | None:
        self.createTables()
        results = self.cur.execute(
            "SELECT MAX(s.sessionId) FROM Session s " +
            "LEFT JOIN Division d ON s.sessionId = d.sessionId " +
            "LEFT JOIN TeamMatch tm ON tm.divisionId = d.divisionId " +
            "LEFT JOIN PlayerMatch pm ON pm.teamMatchId = tm.teamMatchId " +
            f"WHERE pm.memberId1 = {memberId} OR pm.memberId2 = {memberId}"
        ).fetchone()
        if results[0] is None:
            return None
        else:
            return int(results[0])

    

    # ------------------------- Inserting -------------------------
    def addPlayerMatch(self, playerMatch: PlayerMatch) -> None:
        for playerResult in playerMatch.getPlayerResults():
            score = playerResult.getScore()
            try:
                self.cur.execute(
                    f"INSERT INTO Score VALUES (NULL, {score.getTeamPtsEarned()}, {score.getPlayerPtsEarned()}, {score.getPlayerPtsNeeded()})"
                )
            except Exception as e:
                print(e)
                pass

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

        try:
            self.cur.execute(f"DELETE FROM PlayerMatch WHERE teamMatchId = {teamMatchId} and playerMatchId = {playerMatchId}")
            self.cur.execute(
                f"""INSERT INTO PlayerMatch VALUES ({playerMatchId}, {teamMatchId}, {teamId1}, {memberId1}, {skillLevel1}, "NULL", {scoreId1}, {teamId2}, {memberId2}, {skillLevel2}, "NULL", {scoreId2})"""
            )
        except Exception as e:
            print(e)
            pass
        self.con.commit()
    
    def addTeamMatch(self, teamMatchId: int, apaDatetime: str, divisionId: int) -> None:
        try:
            self.cur.execute(f"INSERT INTO TeamMatch VALUES ({teamMatchId}, '{apaDatetime}', {divisionId})")
            
        except Exception:
            pass
        self.con.commit()
    
    def addTempTeamMatch(self, teamMatchId: int, apaDatetime: str, divisionId: int) -> None:
        try:
            self.createTables()
            self.cur.execute(f"INSERT INTO TempTeamMatch VALUES ({teamMatchId}, '{apaDatetime}', {divisionId})")
            
        except Exception:
            pass
        self.con.commit()
    
    def addTeamInfo(self, team: Team) -> None:
        divisionId = team.getDivision().getDivisionId()
        sessionId = team.getDivision().getSession().getSessionId()
        teamId = team.getTeamId()
        teamNum = team.getTeamNum()
        teamName = team.getTeamName()
        self.addTeam(divisionId, teamId, teamNum, teamName)
        #TODO: Delete all currentTeamPlayer entries belonging to the team and re-add all the players
        # That way the table stays current
        format = team.getDivision().getFormat()
        
        for player in team.getPlayers():
            memberId = player.getMemberId()
            playerName = player.getPlayerName()
            currentSkillLevel = player.getCurrentSkillLevel()

            self.addCurrentTeamPlayer(teamId, memberId)
            self.addPlayer(memberId, playerName, currentSkillLevel, sessionId, format)

    def addTeam(self, divisionId: int, teamId: int, teamNum: int, teamName: str) -> None:
        self.createTables()
        try:
            self.cur.execute(
                f"""INSERT INTO Team VALUES ({divisionId}, {teamId}, {teamNum}, "{teamName}")"""
            )
        except Exception as e:
            print(e)
            pass

        self.con.commit()

    def addCurrentTeamPlayer(self, teamId: int, memberId: int) -> None:
        self.createTables()
        try:
            self.cur.execute(
                f"INSERT INTO CurrentTeamPlayer VALUES ({teamId}, {memberId})"
            )
        except Exception as e:
            print(e)
            pass
        self.con.commit()

    def addPlayer(self, memberId: int, playerName: str, currentSkillLevel: int, sessionId: int, format: Format) -> None:
        self.createTables()
        try:
            self.cur.execute(
                f"""INSERT INTO Player VALUES ({memberId}, "{playerName}", {currentSkillLevel})"""
            )
        except Exception:
            mostRecentlyPlayedSessionByPlayer = self.getLastSessionIdPlayedByPlayer(memberId)
            if (mostRecentlyPlayedSessionByPlayer is None or sessionId >= mostRecentlyPlayedSessionByPlayer) and format != Format.MASTERS:
                self.cur.execute(
                    f"""UPDATE Player SET currentSkillLevel = {currentSkillLevel}, playerName = "{playerName}" WHERE memberId = {memberId}"""
                )
        self.con.commit() 

    def addSession(self, session: Session) -> None:
        self.createTables()
        
        try:
            self.cur.execute(f"INSERT INTO Session VALUES ({session.getSessionId()}, '{session.getSessionSeason().value}', {session.getSessionYear()})")
        except Exception:
            pass
        self.con.commit()
    
    def addDivision(self, division: Division) -> None:
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
                f"'{division.getFormat().value}')"
            )
            self.con.commit()  


    # ------------------------- Deleting -------------------------
    def deleteSession(self, sessionId: int) -> None:
        self.deleteDivision(sessionId, None)
        
        self.cur.execute(f"DELETE FROM Session WHERE sessionId = {sessionId}")
        self.con.commit()

    def deleteDivision(self, sessionId: int | None, divisionId: int | None) -> None:
        assert(sessionId is not None or divisionId is not None)
        
        self.deleteTeam(sessionId, divisionId)
        self.deleteTeamMatch(sessionId, divisionId)

        if divisionId is None:
            self.cur.execute(f"DELETE FROM Division WHERE sessionId = {sessionId}")
    
        self.con.commit()

    def deleteTeamMatch(self, sessionId: int | None, divisionId: int | None) -> None:
        assert(sessionId is not None or divisionId is not None)
        
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

    def deleteTempTeamMatch(self, sessionId: int | None, divisionId: int | None) -> None:
        assert(sessionId is not None or divisionId is not None)

        if divisionId is None:
            self.cur.execute(
                "DELETE FROM TempTeamMatch WHERE divisionId IN (" +
                    "SELECT divisionId FROM Division d " +
                    "LEFT JOIN Session s ON s.sessionId = d.sessionId " +
                    f"WHERE s.sessionId = {sessionId}" +
                ")"
            )
        else:
            self.cur.execute(
                f"DELETE FROM TempTeamMatch WHERE divisionId = {divisionId}"
            )
            
        self.con.commit()
    
    def deletePlayerMatch(self, sessionId: int | None, divisionId: int | None) -> None:
        assert(sessionId is not None or divisionId is not None)

        self.deleteScore(sessionId, divisionId)

        if divisionId is None:
            self.cur.execute(
                "DELETE FROM PlayerMatch WHERE teamMatchId IN (" +
                    "SELECT tm.teamMatchId FROM TeamMatch tm " +
                    "LEFT JOIN Division d ON tm.divisionId = d.divisionId " +
                    "LEFT JOIN Session s ON d.sessionId = s.sessionId " +
                    f"WHERE s.sessionId = {sessionId}" +
                ")"
            )
        else:
            self.cur.execute(
                "DELETE FROM PlayerMatch WHERE teamMatchId IN (" +
                    f"SELECT teamMatchId FROM TeamMatch WHERE divisionId = {divisionId}" +
                ")"
            )
        self.con.commit()
    
    def deleteScore(self, sessionId: int | None, divisionId: int | None) -> None:
        assert(sessionId is not None or divisionId is not None)
        
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
    
    def deleteTeam(self, sessionId: int | None, divisionId: int | None) -> None:
        assert(sessionId is not None or divisionId is not None)
        
        self.deleteCurrentTeamPlayer(sessionId, divisionId)
        
        if divisionId is None:
            self.cur.execute(
                "DELETE FROM Team WHERE divisionId IN (" +
                    "SELECT d.divisionId FROM Division d " +
                    "LEFT JOIN Session s ON d.sessionId = s.sessionId " +
                    f"WHERE s.sessionId = {sessionId}" +
                ")"
            )
        else:
            self.cur.execute(f"DELETE FROM Team WHERE divisionId = {divisionId}")
        self.con.commit()
        
    def deleteCurrentTeamPlayer(self, sessionId: int | None, divisionId: int | None) -> None:
        assert(sessionId is not None or divisionId is not None)
        
        if divisionId is None:
            self.cur.execute(
                "DELETE FROM CurrentTeamPlayer WHERE teamId IN (" +
                    "SELECT t.teamId FROM Team t " +
                    "LEFT JOIN Division d ON t.divisionId = d.divisionId " +
                    "LEFT JOIN Session s ON d.sessionId = s.sessionId " +
                    f"WHERE s.sessionId = {sessionId}"
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
    def isValueInTeamMatchTable(self, teamMatchId: int) -> bool:
        return self.cur.execute(f"SELECT COUNT(*) FROM TeamMatch WHERE teamMatchId = {teamMatchId}").fetchone()[0] > 0

    # ------------------------- Counting -------------------------
    def countPlayerMatches(self) -> int:
        return self.cur.execute("SELECT COUNT(*) FROM PlayerMatch").fetchone()[0]

    
    # ------------------------- Adjusted Skill Level -------------------------
    def updateASL(self, playerMatchId: int, teamMatchId: int, adjustedSkillLevel: float, playerResultId: int) -> None:
        self.cur.execute(
            "UPDATE PlayerMatch " +
            f"SET adjustedSkillLevel{playerResultId + 1} = {adjustedSkillLevel} " +
            f"WHERE playerMatchId = {playerMatchId} AND teamMatchId = {teamMatchId}"
        )
        self.con.commit()
    