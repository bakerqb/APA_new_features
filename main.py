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
from src.dataClasses.Criteria import Criteria
from src.dataClasses.PotentialTeamMatch import PotentialTeamMatch

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
    divisionId = request.args.get('divisionId')
    sessionId = request.args.get('sessionId')
    # return useCase.getTeamResultsJson("SPRING", 2024, teamName, True)

    jsonObj = useCase.getTeamResultsJson(teamId, True) | { "divisionId": divisionId, "sessionId": sessionId}

    # TODO: fix the parameters for getTeamResultsJson
    return render_template(
        jinja_environment.get_template('results.html'),
        url_for=url_for,
        **jsonObj
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
    sessionId = request.args.get('sessionId')
    divisionId = request.args.get('divisionId')
    db = Database()
    db.deleteDivision(None, divisionId)
    return redirect(f"/division?sessionId={sessionId}&divisionId={divisionId}")

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
    putupMemberId = request.args.get('putupMemberId')
    sessionId = request.args.get('sessionId')
    divisionId = request.args.get('divisionId')

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

    putupPlayer = None
    if putupMemberId is not None:
        putupPlayer = converter.toPlayerWithSql(db.getPlayerBasedOnMemberId(putupMemberId))

    
    teamMatchup = TeamMatchup(team1, team2, putupPlayer)
    potentialTeamMatch = teamMatchup.start()
    jsonObj = {
        "potentialTeamMatch": potentialTeamMatch,
        "team1": team1,
        "team2": team2,
        "doesTeam1PutUpFirst": putupMemberId is None,
        "sessionId": sessionId,
        "divisionId": divisionId
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
    sessionId = request.args.get('sessionId')
    divisionId = request.args.get('divisionId')


    db = Database()
    converter = Converter()
    team1 = converter.toTeamWithSql(db.getTeamWithTeamId(teamId1))
    team2 = converter.toTeamWithSql(db.getTeamWithTeamId(teamId2))
    division = converter.toDivisionWithSql(db.getDivision(divisionId))
    jsonObj = {
        "team1": team1,
        "team2": team2,
        "division": division
    }
    
    return render_template(
        jinja_environment.get_template('matchupTeams.html'),
        url_for=url_for,
        **jsonObj
    )

@app.route("/players")
def players():
    memberId = request.args.get('memberId')
    playerName = request.args.get('playerName')
    minSkillLevel = request.args.get('minSkillLevel')
    maxSkillLevel = request.args.get('maxSkillLevel')
    dateLastPlayed = request.args.get('dateLastPlayed')

    db = Database()
    converter = Converter()
    criteria = Criteria(memberId, playerName, minSkillLevel, maxSkillLevel, dateLastPlayed)
    jsonObj = { "players": db.getPlayers(criteria) }
    
    return render_template(
        jinja_environment.get_template('players.html'),
        url_for=url_for,
        **jsonObj
    )


    

@app.route("/session")
def session():
    useCase = UseCase()
    sessionId = request.args.get('sessionId')
    db = Database()
    converter = Converter()
    session = converter.toSessionWithSql(db.getSession(sessionId)[0])
    context = {
        "session": session,
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

@app.route("/playerMatches")
def playerMatches():
    useCase = UseCase()
    memberId = request.args.get('memberId')
    return render_template(
        jinja_environment.get_template('player.html'),
        url_for=url_for,
        **useCase.getPlayerMatchesForPlayerJson(memberId)
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

@app.route("/test")
def test():
    apaWebScraper = ApaWebScraper()
    db = Database()
    db.deleteDivision(None, 208953)
    apaWebScraper.scrapeAllEightBallThursDivisions()

if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=8000)