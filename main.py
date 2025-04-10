import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.srcMain.Database import Database
from src.srcMain.ApaWebScraper import ApaWebScraper
from src.srcMain.TeamMatchup import TeamMatchup
from waitress import serve
from flask import Flask, render_template, request, url_for, redirect
import jinja2
from src.dataClasses.SearchCriteria import SearchCriteria
from src.dataClasses.TeamMatchCriteria import TeamMatchCriteria
from src.exceptions.InvalidTeamMatchCriteria import InvalidTeamMatchCriteria
from src.srcMain.DataFetcher import DataFetcher
from src.converter.PotentialTeamMatchConverter import PotentialTeamMatchConverter
from src.utils.aslMatrix import *

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))


@app.route("/results")
def results():
    dataFetcher = DataFetcher()
    teamId = int(request.args.get('teamId'))
    divisionId = int(request.args.get('divisionId'))
    sessionId = int(request.args.get('sessionId'))

    data = { 
        "teamResults": dataFetcher.getTeamResults(teamId),
        "divisionId": divisionId,
        "sessionId": sessionId
    }

    return render_template(
        jinja_environment.get_template('results.html'),
        url_for=url_for,
        format=format,
        int=int,
        str=str,
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
    sessionId = int(request.args.get('sessionId'))
    apaWebScraper = ApaWebScraper()
    apaWebScraper.scrapeDivisionsForSession(sessionId)
    return redirect(f"/session?sessionId={sessionId}")

@app.route("/scrapeDivision")
def scrapeDivision():
    sessionId = int(request.args.get('sessionId'))
    divisionId = int(request.args.get('divisionId'))
    apaWebScraper = ApaWebScraper()
    apaWebScraper.scrapeDivision(divisionId)
    return redirect(f"/division?sessionId={sessionId}&divisionId={divisionId}")

@app.route("/deleteDivision")
def deleteDivision():
    sessionId = int(request.args.get('sessionId'))
    divisionId = int(request.args.get('divisionId'))
    db = Database()
    db.deleteDivision(None, divisionId)
    return redirect(f"/division?sessionId={sessionId}&divisionId={divisionId}")

@app.route("/deleteSession")
def deleteSession():
    sessionId = int(request.args.get('sessionId'))
    db = Database()
    db.deleteSession(sessionId)
    return redirect("/home1")

@app.route("/matchups")
def matchups():
    dataFetcher = DataFetcher()

    teamId1 = int(request.args.get('teamId1'))
    teamId2 = int(request.args.get('teamId2'))
    putupMemberId = request.args.get('putupMemberId')
    if putupMemberId is not None:
        putupMemberId = int(putupMemberId)
    sessionId = int(request.args.get('sessionId'))
    divisionId = int(request.args.get('divisionId'))
    matchNumber = int(request.args.get('matchNumber'))
    teamMatchCriteriaRawData = request.args.getlist('teamMatchCriteria')

    format_ = dataFetcher.getFormatForDivision(divisionId)
    team1 = dataFetcher.getTeam(None, None, teamId1)
    team2 = dataFetcher.getTeam(None, None, teamId2)

    teamPlayerPairings = []
    for key in list(request.args.keys()):
        if "-" in key:
            teamPlayerPairings.append(key)
    
    try:
        team1memberIds, team2memberIds = keysToTeams(teamPlayerPairings)
    except InvalidTeamMatchCriteria:
        return redirect(f"/matchupTeams?teamId1={teamId1}&teamId2={teamId2}&sessionId={sessionId}&divisionId={divisionId}")
    
    team1Roster = list(map(lambda memberId: dataFetcher.getPlayer(None, None, memberId), team1memberIds))
    team2Roster = list(map(lambda memberId: dataFetcher.getPlayer(None, None, memberId), team2memberIds))
    team1.setPlayers(team1Roster)
    team2.setPlayers(team2Roster)
    putupPlayer = dataFetcher.getPlayer(None, None, putupMemberId) if putupMemberId is not None else None
    
    try:
        teamMatchCriteria = TeamMatchCriteria(teamMatchCriteriaRawData, team1, team2, matchNumber, putupPlayer)
        teamMatchup = TeamMatchup(team1, team2, putupPlayer, matchNumber, format_)
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
        str=str,
        format=format,
        int=int,
        **data
    )

def keysToTeams(keys):
    if len(keys) == 0:
        raise InvalidTeamMatchCriteria("ERROR: No players selected")
    teamId1 = int(keys[0].split('-')[0])
    teamRoster1 = []
    teamRoster2 = []
    for key in keys:
        key = key.replace('-double-play', '') 
        teamId, memberId = key.split('-')
        teamId = int(teamId)
        memberId = int(memberId)
        if teamId == teamId1:
            teamRoster1.append(memberId)
        else:
            teamRoster2.append(memberId)
    return (teamRoster1, teamRoster2)


@app.route("/matchupTeams")
def matchupTeams():
    teamId1 = int(request.args.get('teamId1'))
    teamId2 = int(request.args.get('teamId2'))
    sessionId = int(request.args.get('sessionId'))
    divisionId = int(request.args.get('divisionId'))

    dataFetcher = DataFetcher()
    team1 = dataFetcher.getTeam(None, None, teamId1)
    team2 = dataFetcher.getTeam(None, None, teamId2)
    division = dataFetcher.getDivision(divisionId)

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
    if memberId == '' or memberId is None:
        memberId = None
    else:
        memberId = int(memberId)
    playerName = request.args.get('playerName')
    minSkillLevel = request.args.get('minSkillLevel')
    if minSkillLevel == '' or minSkillLevel is None:
        minSkillLevel = None
    else:
        minSkillLevel = int(minSkillLevel)
    maxSkillLevel = request.args.get('maxSkillLevel')
    if maxSkillLevel == '' or maxSkillLevel is None:
        maxSkillLevel = None
    else:
        maxSkillLevel = int(maxSkillLevel)
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
    dataFetcher = DataFetcher()
    sessionId = int(request.args.get('sessionId'))
    session = dataFetcher.getSession(sessionId)
    divisions = dataFetcher.getDivisions(sessionId)
    data = {
        "session": session,
        "divisions": divisions
    }
    return render_template(
        jinja_environment.get_template('session.html'),
        url_for=url_for,
        **data
    )

@app.route("/home1")
def home1():
    dataFetcher = DataFetcher()
    data = {
        "sessions": dataFetcher.getSessions()
    }
    
    return render_template(
        jinja_environment.get_template('home1.html'),
        url_for=url_for,
        **data
    )

@app.route("/playerMatches")
def playerMatches():
    memberId = int(request.args.get('memberId'))
    dataFetcher = DataFetcher()

    player = dataFetcher.getPlayer(None, None, memberId)
    format = dataFetcher.getConfigFormat()
    playerMatches = dataFetcher.getPlayerMatches(None, None, None, memberId, format, None, None, None, None, None, player, True)
    data = {
        "player": player,
        "playerMatches": playerMatches
    }

    return render_template(
        jinja_environment.get_template('player.html'),
        url_for=url_for,
        **data
    )


@app.route("/division")
def division():
    dataFetcher = DataFetcher()
    divisionId = int(request.args.get('divisionId'))

    division = dataFetcher.getDivision(divisionId)
    teams = dataFetcher.getTeams(division)
    shouldDisplayTeamMatchupFeature = dataFetcher.shouldDisplayTeamMatchupFeature(divisionId)
    data = {
        "teams": teams,
        "division": division,
        "shouldDisplayTeamMatchupFeature": shouldDisplayTeamMatchupFeature
    }

    return render_template(
        jinja_environment.get_template('division.html'),
        url_for=url_for,
        **data
    )

@app.route("/predictionAccuracy")
def predictionAccuracy():
    dataFetcher = DataFetcher()
    potentialTeamMatchConverter = PotentialTeamMatchConverter()
    format = dataFetcher.getConfigFormat()
    teamMatches = dataFetcher.getTeamMatchesWithoutASL(None, None, None, None, format, None, None, None, None, None)

    numCorrectlyPredictedMatches = 0
    numTeamMatchesNotResultingInTie = len(teamMatches)
    skillLevelMatrix = createASLMatrix(format, dataFetcher.getExpectedPtsMethod())

    # For each of the teamMatches:
    #   Determine who actually won the match
    #   Create PotentialTeamMatch with the actual matchups including the expected points value for each matchup
    #   If the team expected to win actually won, increase the counter by 1
    for teamMatch in teamMatches:
        actualWinningTeams = teamMatch.getWinningTeams()
        if len(actualWinningTeams) == 2:
            numTeamMatchesNotResultingInTie -= 1
            continue
        else:
            actualWinningTeam = actualWinningTeams[0]
            potentialTeamMatch = potentialTeamMatchConverter.toPotentialTeamMatchFromTeamMatch(teamMatch, skillLevelMatrix, format)
            expectedWinningTeams = potentialTeamMatch.getExpectedWinningTeams()
            if len(expectedWinningTeams) == 2:
                numTeamMatchesNotResultingInTie -= 1
                continue
            else: 
                expectedWinningTeam = expectedWinningTeams[0]
                if actualWinningTeam == expectedWinningTeam:
                    numCorrectlyPredictedMatches += 1
        
    correctlyPredictedPercentage = numCorrectlyPredictedMatches/numTeamMatchesNotResultingInTie
    return str(correctlyPredictedPercentage)

@app.route("/mvp")
def getMostValuableSkillLevels():
    dataFetcher = DataFetcher()
    skillLevelMatrix = createASLMatrix(dataFetcher.getConfigFormat(), dataFetcher.getExpectedPtsMethod())
    return getMostValuableASLSkillLevels(skillLevelMatrix)

if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=8000)