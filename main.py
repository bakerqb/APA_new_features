import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.srcMain.UseCase import UseCase
from src.srcMain.Database import Database
from src.srcMain.ApaWebScraper import ApaWebScraper
from src.srcMain.TeamMatchup import TeamMatchup
from src.converter.Converter import Converter
from waitress import serve
from flask import Flask, render_template, request, url_for, redirect
import jinja2
from src.dataClasses.SearchCriteria import SearchCriteria
from src.dataClasses.TeamMatchCriteria import TeamMatchCriteria
from src.dataClasses.Format import Format
from src.exceptions.InvalidTeamMatchCriteria import InvalidTeamMatchCriteria

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))


@app.route("/results")
def results():
    useCase = UseCase()
    teamId = request.args.get('teamId')
    divisionId = request.args.get('divisionId')
    sessionId = request.args.get('sessionId')

    data = { 
        "teamResults": useCase.getTeamResults(teamId, True),
        "divisionId": divisionId,
        "sessionId": sessionId
    }

    return render_template(
        jinja_environment.get_template('results.html'),
        url_for=url_for,
        **data
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
    matchNumber = int(request.args.get('matchNumber'))
    format = db.getFormat(divisionId)

    team1 = converter.toTeamWithSql(db.getTeamWithTeamId(teamId1))
    team2 = converter.toTeamWithSql(db.getTeamWithTeamId(teamId2))

    teamPlayerPairings = []
    for key in list(request.args.keys()):
        if "-" in key:
            teamPlayerPairings.append(key)
    
    try:
        team1memberIds, team2memberIds = keysToTeams(teamPlayerPairings)
    except InvalidTeamMatchCriteria:
        return redirect(f"/matchupTeams?teamId1={teamId1}&teamId2={teamId2}&sessionId={sessionId}&divisionId={divisionId}")
    
    team1Roster = list(map(lambda memberId: converter.toPlayerWithSql(db.getPlayerBasedOnMemberId(memberId)), team1memberIds))
    team2Roster = list(map(lambda memberId: converter.toPlayerWithSql(db.getPlayerBasedOnMemberId(memberId)), team2memberIds))
    team1.setPlayers(team1Roster)
    team2.setPlayers(team2Roster)

    putupPlayer = None
    if putupMemberId is not None:
        putupPlayer = converter.toPlayerWithSql(db.getPlayerBasedOnMemberId(putupMemberId))
    try:
        teamMatchCriteria = TeamMatchCriteria(request.args.getlist('teamMatchCriteria'), team1, team2, matchNumber, putupPlayer)
        teamMatchup = TeamMatchup(team1, team2, putupPlayer, matchNumber, format)
    except InvalidTeamMatchCriteria:
        return redirect(f"/matchupTeams?teamId1={teamId1}&teamId2={teamId2}&sessionId={sessionId}&divisionId={divisionId}")
    
    potentialTeamMatch = teamMatchup.start(teamMatchCriteria, matchNumber)
    data = {
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
        **data
    )

def keysToTeams(keys):
    if len(keys) == 0:
        raise InvalidTeamMatchCriteria("ERROR: No players selected")
    teamId1 = keys[0].split('-')[0]
    teamRoster1 = []
    teamRoster2 = []
    for key in keys:
        key = key.replace('-double-play', '') 
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
    data = {
        "team1": team1,
        "team2": team2,
        "division": division
    }
    
    return render_template(
        jinja_environment.get_template('matchupTeams.html'),
        url_for=url_for,
        **data
    )

@app.route("/players")
def players():
    memberId = request.args.get('memberId')
    playerName = request.args.get('playerName')
    minSkillLevel = request.args.get('minSkillLevel')
    maxSkillLevel = request.args.get('maxSkillLevel')
    dateLastPlayed = request.args.get('dateLastPlayed')

    db = Database()
    searchCriteria = SearchCriteria(memberId, playerName, minSkillLevel, maxSkillLevel, dateLastPlayed)
    data = { "players": db.getPlayers(searchCriteria) }
    
    return render_template(
        jinja_environment.get_template('players.html'),
        url_for=url_for,
        **data
    )

@app.route("/session")
def session():
    useCase = UseCase()
    sessionId = request.args.get('sessionId')
    db = Database()
    converter = Converter()
    session = converter.toSessionWithSql(db.getSession(sessionId)[0])
    data = {
        "session": session,
        "divisions": useCase.getDivisions(sessionId)
    }
    return render_template(
        jinja_environment.get_template('session.html'),
        url_for=url_for,
        **data
    )

@app.route("/home1")
def home1():
    useCase = UseCase()
    return render_template(
        jinja_environment.get_template('home1.html'),
        url_for=url_for,
        **useCase.getSessions()
    )

@app.route("/playerMatches")
def playerMatches():
    useCase = UseCase()
    memberId = request.args.get('memberId')
    return render_template(
        jinja_environment.get_template('player.html'),
        url_for=url_for,
        **useCase.getPlayerMatchesForPlayer(memberId)
    )


@app.route("/division")
def division():
    useCase = UseCase()
    db = Database()
    converter = Converter()
    divisionId = request.args.get('divisionId')
    format = db.getFormat(divisionId)
    sessionInQuestion = converter.toDivisionWithSql(db.getDivision(divisionId)).getSession()
    mostRecentSession = converter.toSessionWithSql(db.getSession(db.getMostRecentSessionId(format))[0])
    previousSession = mostRecentSession.getPreviousSession()
    displayTeamMatchupFeature = sessionInQuestion == mostRecentSession or sessionInQuestion == previousSession

    return render_template(
        jinja_environment.get_template('division.html'),
        url_for=url_for,
        displayTeamMatchupFeature=displayTeamMatchupFeature,
        **useCase.getTeams(divisionId)
    )

@app.route("/predictionAccuracy")
def predictionAccuracy():
    useCase = UseCase()
    return useCase.getPredictionAccuracy()

if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=8000)