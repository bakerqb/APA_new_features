from src.srcMain.ApaWebScraper import ApaWebScraper
from src.srcMain.Config import Config
from src.srcMain.Database import Database
from converter.Converter import Converter
from dataClasses.TeamResults import TeamResults
from datetime import datetime
import json

class UseCase:
    def __init__(self):
        self.apaWebScraper = ApaWebScraper()
        self.config = Config()
        self.db = Database()
        self.converter = Converter()


    ############### Game agnostic functions ###############
    
    # ------------------------- Printing -------------------------
    def printTeamResults(self, sessionSeason, sessionYear, teamName, isEightBall) -> None:
        self.getTeamResults(sessionSeason, sessionYear, teamName, isEightBall).printPlayerMatchesPerPlayer()

    def printUpcomingTeamResults(self) -> None:
        sessionSeason = self.config.get('session_season_in_question')
        sessionYear = self.config.get('session_year_in_question')
        isEightBall = self.isEightBallUpcoming()
        sessionConfig = self.config.getSessionConfig(isEightBall)
        teamName = self.apaWebScraper.getOpponentTeamName(sessionConfig.get('my_team_name'), sessionConfig.get('division_link'))
        self.printTeamResults(sessionSeason, sessionYear, teamName, isEightBall)

    def printUpcomingTeamResultsJson(self) -> None:
        self.printTeamResultsJson(self.getUpcomingTeamResultsJson())

    def printTeamResultsJson(self, sessionSeason, sessionYear, teamName, isEightBall) -> None:
        teamResults = self.getTeamResults(sessionSeason, sessionYear, teamName, isEightBall).toJson()
        file = open('src/resources/teamResults.json', 'w')
        file.write(json.dumps(teamResults, indent=2))

    # ------------------------- Scraping -------------------------
    def scrapeUpcomingTeamResults(self) -> None:
        isEightBall = self.isEightBallUpcoming()
        sessionConfig = self.config.getSessionConfig(isEightBall)
        self.apaWebScraper.scrapeDivision(sessionConfig.get('division_link'), isEightBall)

    # ------------------------- Getting -------------------------
    def getUpcomingTeamResultsJson(self) -> dict:
        isEightBall = self.isEightBallUpcoming()
        sessionSeason = self.config.getConfig().get('session_season_in_question')
        sessionYear = self.config.getConfig().get('session_year_in_question')
        sessionConfig = self.config.getSessionConfig(isEightBall)
        teamName = self.apaWebScraper.getOpponentTeamName(sessionConfig.get('my_team_name'), sessionConfig.get('division_link'))
        return self.getTeamResultsJson(sessionSeason, sessionYear, teamName, isEightBall)

    def getTeamResultsJson(self, sessionSeason, sessionYear, teamName, isEightBall) -> dict:
        return self.getTeamResults(sessionSeason, sessionYear, teamName, isEightBall).toJson()
    
    def getTeamResults(self, sessionSeason, sessionYear, teamName, isEightBall) -> dict:
        teamResultsDb = self.db.getTeamResults(sessionSeason, sessionYear, teamName, isEightBall)
        teamResultsPlayerMatches = list(map(lambda playerMatch: self.converter.toPlayerMatchWithSql(playerMatch, isEightBall), teamResultsDb))
        return TeamResults(teamName, sessionSeason, sessionYear, isEightBall,
                                                self.db.getTeamRoster(sessionSeason, sessionYear, teamName, isEightBall),
                                                teamResultsPlayerMatches)

    # ------------------------- Helper functions -------------------------
    def isEightBallUpcoming(self) -> bool:
        today_weekday = datetime.now().weekday()
        monday_weekday = 0
        thursday_weekday = 3
        num_days_in_week = 7
        return (thursday_weekday - today_weekday) % num_days_in_week < (monday_weekday - today_weekday) % num_days_in_week
    
    

    ############### 9 Ball functions ###############

    def scrapeAllNineBallSessionLinks(self) -> None:
        sessions_with_no_data = [89, 91, 92, 93, 100, 101, 105, 106, 110, 114, 115, 116, 120, 121, 122, 126, 127, 128, 131, 132]
        starting_session = self.config.get('apa_website').get('starting_session')
        current_session = self.config.get('apa_website').get('current_session')
        if self.db.isNineBallDivisionTableFull(current_session - starting_session - len(sessions_with_no_data) + 1):
            print("NineBallDivision table up to date. No scraping needed")
            return
        
        for sessionId in range(starting_session, current_session + 1):
            if sessionId in sessions_with_no_data:
                continue
            
            self.apaWebScraper.scrapeSessionLink(sessionId)

    def scrapeAllNineBallData(self) -> None:
        self.scrapeAllSessionLinks()
        for divisionLink in self.db.getNineBallDivisionLinks():
            self.apaWebScraper.scrapeDivision(divisionLink, False)
    
    def scrapeCurrentNineBallSessionData(self) -> None:
        division_link = self.config.getConfig().get('nine_ball_data').get('division_link')
        self.apaWebScraper.scrapeDivision(division_link, False)

    def getNineBallMatrix(self) -> None:
        self.db.createNineBallMatrix()

    def getNineBallMatrixMedian(self) -> None:
        self.db.createNineBallMatrixMedian()
    

    ############### 8 Ball functions ###############

    def printEightBallTeamResultsAfterNameChange(self, sessionSeason: str, sessionYear: int, teamNames: list[str]) -> None:
        playerMatches = []
        for teamName in teamNames:
            playerMatches += self.db.getTeamResults(sessionSeason, sessionYear, teamName, True)
        
        playerMatchObjList = []
        for playerMatch in playerMatches:
            playerMatchObjList.append(self.converter.toPlayerMatchWithSql(playerMatch, True))
        roster = self.db.getTeamRoster(sessionSeason, sessionYear, teamName, True)
        
        playerMatchMap = {}
        for player in roster:
            playerMatchMap[player[0]] = []

        for playerMatchObj in playerMatchObjList:
            for player in roster:
                if playerMatchObj.isPlayedBy(player[0]):
                    playerMatchMap[player[0]].append(playerMatchObj)

        for playerName in playerMatchMap.keys():
            self.printPlayerMatchesForPlayer(playerName, playerMatchMap[playerName])
