import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main.UseCase import UseCase
from src.main.Database import Database
from src.main.ApaWebScraper import ApaWebScraper
from src.main.Config import Config
from waitress import serve
from flask import Flask, render_template, request, url_for


import jinja2

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')))

app = Flask(__name__)


@app.route("/results")
def results():
    csslink = url_for('static', filename='css/styles.css')
    config = Config()
    useCase = UseCase()
    apaWebScraper = ApaWebScraper()
    db = Database()
    teamName = request.args.get('teamName')

    template = jinja_environment.get_template('results.html')

    return useCase.getTeamResultsJson("SPRING", 2024, teamName, True)

    return render_template(
        template,
        csslink=csslink,
        **useCase.getTeamResultsJson("SPRING", 2024, teamName, True)
    )

@app.route("/home")
def home():
    csslink = url_for('static', filename='styles.css')
    config = Config()
    useCase = UseCase()
    apaWebScraper = ApaWebScraper()
    db = Database()

    teamName = "The Final Boss"
    template = jinja_environment.get_template('index.html')

    return render_template(
        "index.html",
        **useCase.getTeamResultsJson("SPRING", 2024, teamName, True)
    )
    

if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=8000)