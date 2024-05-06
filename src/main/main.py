from UseCase import UseCase
from Database import Database
from ApaWebScraper import ApaWebScraper
from Config import Config


def main():
    config = Config()
    useCase = UseCase()
    apaWebScraper = ApaWebScraper()
    db = Database()

    # useCase.scrapeCurrentNineBallSessionData()
    # useCase.getNineBallMatrix()
    
    # db.deleteNineBallSeason()

    # useCase.getUpcomingTeamResults()
    # useCase.printUpcomingTeamResults()

    useCase.printUpcomingTeamResultsJson()

    # useCase.printEightBallTeamResultsAfterNameChange("SPRING", 2024, ["The Final Boss", "Sir-Scratch-A Lot"])
    # for item in db.getRubbishMatches():
    #     print(item)
    

if __name__ == "__main__":
    main()