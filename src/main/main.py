from UseCase import UseCase
from Database import Database
from ApaWebScraper import ApaWebScraper
from Config import Config


def main():
    config = Config()
    useCase = UseCase()
    apaWebScraper = ApaWebScraper()
    db = Database()

    
    # useCase.getNineBallMatrix()
    
    # db.deleteNineBallSeason()

    # useCase.scrapeUpcomingTeamResults()
    # useCase.printUpcomingTeamResults()
    # db.deleteSessionData()
    # useCase.scrapeCurrentNineBallSessionData()
    useCase.printTeamResultsJson("SPRING", 2024, "Miniclip", False)


    # useCase.printEightBallTeamResultsAfterNameChange("SPRING", 2024, ["The Final Boss", "Sir-Scratch-A Lot"])
    # for item in db.getRubbishMatches():
    #     print(item)
    

if __name__ == "__main__":
    main()