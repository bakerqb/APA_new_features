# Getting Results of APA Team
The purpose of this app is to list the match scores for an APA team so you can see how each player has been performing this season. 

## To run:
### Setup
1. Create a Python virtual environment by running `python3 -m venv env`
2. Activate the virtual environment by running `source env/bin/activate` 
3. Run `pip3 install -r requirements.txt` to install necessary Python libraries
### Inserting team and player information
1. Open the application.yml file. This is where you will list the division and player and/or team you want to look up.
2. Insert the link for your division here. You will need to go to the APA website to retrieve this URL
3. Insert the name of the team you want to look up
4. Insert your APA credentials at the bottom of this file. The application.yml file is included in the .gitignore, but PLEASE DO NOT ACCIDENTALLY PUSH YOUR APA CREDENTIALS TO THIS REPO
5. Run `python3 converter.py`
