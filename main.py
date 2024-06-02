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
    teamName = request.args.get('teamName')
    # return useCase.getTeamResultsJson("SPRING", 2024, teamName, True)

    # TODO: fix the parameters for getTeamResultsJson
    return render_template(
        jinja_environment.get_template('results.html'),
        url_for=url_for,
        **useCase.getTeamResultsJson("SPRING", 2024, teamName, True)
    )

@app.route("/home", methods=['GET'])
def home():
    return render_template(
        jinja_environment.get_template('index.html'),
        url_for=url_for
    )

@app.route("/test")
def test():
    useCase = UseCase()
    db = Database()
    #db.refreshAllTables(True)
    #useCase.scrapeUpcomingTeamResults()
    
    # TODO: put in these values and test it out!!!
    return useCase.getTeamResultsJson(132, 245, 12437619)

    

if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=8000)