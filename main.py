import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.srcMain.UseCase import UseCase
from src.srcMain.Database import Database
from src.srcMain.ApaWebScraper import ApaWebScraper
from src.srcMain.Config import Config
from waitress import serve
from flask import Flask, render_template, request, url_for
import jinja2

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
print(__name__)
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))


@app.route("/results")
def results():
    config = Config()
    useCase = UseCase()
    apaWebScraper = ApaWebScraper()
    db = Database()
    teamId = request.args.get('teamId')
    # return useCase.getTeamResultsJson("SPRING", 2024, teamName, True)

    # TODO: fix the parameters for getTeamResultsJson
    return render_template(
        jinja_environment.get_template('results.html'),
        url_for=url_for,
        **useCase.getTeamResultsJson(teamId, True)
    )

@app.route("/index", methods=['GET'])
def home():
    return render_template(
        jinja_environment.get_template('index.html'),
        url_for=url_for
    )

@app.route("/test")
def test():
    useCase = UseCase()
    db = Database()
    db.refreshAllTables(True)
    useCase.scrapeUpcomingTeamResults()
    print("Done scraping")
    # TODO: put in these values and test it out!!!
    return render_template(
        jinja_environment.get_template('results.html'),
        url_for=url_for,
        **useCase.getTeamResultsJson(12437618)
    )

@app.route("/session")
def session():
    useCase = UseCase()
    sessionId = request.args.get('sessionId')
    context = {
        "sessionId": sessionId,
        "divisions": useCase.getDivisionsJson(sessionId)
    }
    return render_template(
        jinja_environment.get_template('session.html'),
        url_for=url_for,
        **context
    )

@app.route("/home1")
def home1():
    useCase = UseCase()
    return render_template(
        jinja_environment.get_template('home1.html'),
        url_for=url_for,
        **useCase.getSessionsJson()
    )

@app.route("/division")
def division():
    useCase = UseCase()
    sessionId = request.args.get('sessionId')
    divisionId = request.args.get('divisionId')
    return render_template(
        jinja_environment.get_template('division.html'),
        url_for=url_for,
        **useCase.getTeamsJson(sessionId, divisionId)
    )

@app.route("/adjusted-skill-level")
def adjustedSkillLevel():
    useCase = UseCase()
    playerName = request.args.get('playerName')
    currentSkillLevel = int(request.args.get('sl'))
    return useCase.getAdjustedSkillLevel(playerName, currentSkillLevel)

if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=8000)