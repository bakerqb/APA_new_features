import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.srcMain.UseCase import UseCase
from src.srcMain.Database import Database
from src.srcMain.ApaWebScraper import ApaWebScraper
from src.srcMain.Config import Config
from src.srcMain.TeamMatchup import TeamMatchup
from src.converter.Converter import Converter
from waitress import serve
from flask import Flask, render_template, request, url_for, redirect
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

@app.route("/scrapeSession")
def scrapeSession():
    sessionId = request.args.get('sessionId')
    apaWebScraper = ApaWebScraper()
    apaWebScraper.scrapeDivisionsForSession(sessionId)
    return redirect(f"/session?sessionId={sessionId}")

@app.route("/scrapeDivision")
def scrapeDivision():
    sessionId = request.args.get('sessionId')
    divisionId = request.args.get('divisionId')
    apaWebScraper = ApaWebScraper()
    apaWebScraper.scrapeDivision(divisionId)
    return redirect(f"/division?sessionId={sessionId}&divisionId={divisionId}")

@app.route("/deleteDivision")
def deleteDivision():
    divisionId = request.args.get('divisionId')
    db = Database()
    db.deleteDivision(None, divisionId)
    return redirect(f"/division?divisionId={divisionId}")

@app.route("/deleteSession")
def deleteSession():
    sessionId = request.args.get('sessionId')
    db = Database()
    db.deleteSession(sessionId)
    return redirect("/home1")

@app.route("/matchups")
def matchups():
    db = Database()
    converter = Converter()
    teamId1 = request.args.get('teamId1')
    teamId2 = request.args.get('teamId2')

    team1 = converter.toTeamWithSql(db.getTeamWithTeamId(teamId1))
    team2 = converter.toTeamWithSql(db.getTeamWithTeamId(teamId2))

    teamPlayerPairings = []
    for key in list(request.args.keys()):
        if "-" in key:
            teamPlayerPairings.append(key)
    
    team1memberIds, team2memberIds = keysToTeams(teamPlayerPairings)
    team1Roster = list(map(lambda memberId: converter.toPlayerWithSql(db.getPlayerBasedOnMemberId(memberId)), team1memberIds))
    team2Roster = list(map(lambda memberId: converter.toPlayerWithSql(db.getPlayerBasedOnMemberId(memberId)), team2memberIds))
    team1.setPlayers(team1Roster)
    team2.setPlayers(team2Roster)

    db = Database()
    converter = Converter()

    
    teamMatchup = TeamMatchup(team1, team2, True)
    bestMatchups, ptsExpected =  teamMatchup.decideBestMatchups()
    jsonObj = {
        "bestMatchups": bestMatchups,
        "ptsExpected": ptsExpected
    }
    
    return render_template(
        jinja_environment.get_template('matchups.html'),
        url_for=url_for,
        **jsonObj
    )

def keysToTeams(keys):
    teamId1 = keys[0].split('-')[0]
    teamRoster1 = []
    teamRoster2 = []
    for key in keys:
        teamId, memberId = key.split('-')
        if teamId == teamId1:
            teamRoster1.append(memberId)
        else:
            teamRoster2.append(memberId)
    return (teamRoster1, teamRoster2)


@app.route("/matchupTeams")
def matchupTeams():
    teamId1 = request.args.get('teamId1')
    teamId2 = request.args.get('teamId2')

    db = Database()
    converter = Converter()
    team1 = converter.toTeamWithSql(db.getTeamWithTeamId(teamId1))
    team2 = converter.toTeamWithSql(db.getTeamWithTeamId(teamId2))
    jsonObj = {
        "team1": team1,
        "team2": team2
    }
    
    return render_template(
        jinja_environment.get_template('matchupTeams.html'),
        url_for=url_for,
        **jsonObj
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
    divisionId = request.args.get('divisionId')
    return render_template(
        jinja_environment.get_template('division.html'),
        url_for=url_for,
        **useCase.getTeamsJson(divisionId)
    )

if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=8000)