from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from getpass import getpass
from Config import Config
from PlayerMatch import PlayerMatch
from utils.utils import color_plain_text


def main():
    config = Config().get_config()
    driver = webdriver.Chrome()

    # Login to APA portal
    login(driver, config)

    home_page(driver, config)


def login(driver, config):
    
    # Go to signin page
    driver.get(config.get('apa_website').get('login_link'))
    driver.implicitly_wait(config.get('wait_times').get('implicit_wait_time'))

    # Login
    username_element = driver.find_element(By.ID, 'email')
    username_element.send_keys(config.get('apa_credentials').get('email'))
    password_element = driver.find_element(By.ID, 'password')
    password_element.send_keys(config.get('apa_credentials').get('password'))
    password_element.send_keys(Keys.ENTER)
    driver.implicitly_wait(config.get('wait_times').get('implicit_wait_time'))
    time.sleep(config.get('wait_times').get('sleep_time'))
    continue_link = driver.find_element(By.XPATH, "//button[text()='Continue']")
    print("found continue link")
    continue_link.click()

    no_thanks_button = driver.find_element(By.XPATH, "//a[text()='No Thanks']")
    no_thanks_button.click()


def home_page(driver, config):
    driver.get(config.get('apa_website').get('division_link'))
    driver.implicitly_wait(config.get('wait_times').get('implicit_wait_time'))
    time.sleep(5)
    table = driver.find_element(By.TAG_NAME, "tbody")
    
    # Click on team of player in question
    navigate_to_team_page(table, config.get('team_in_question'))
    driver.implicitly_wait(config.get('wait_times').get('implicit_wait_time'))
    
    matches_header = driver.find_element(By.XPATH, "//h2 [contains( text(), 'Team Schedule & Results')]")
    driver.implicitly_wait(config.get('wait_times').get('implicit_wait_time'))
    matches = matches_header.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "a")
    
    
    match_links = []
    for match in matches:
        if '|' in match.text:
            match_links.append(match.get_attribute("href"))
    
    team_results = get_team_results(driver, config, match_links)
    for player in team_results.keys():
        
        print(color_plain_text("\n-------------------- Results for {} --------------------".format(player)))
        i = 1
        for player_match in team_results[player]:
            print("------ Match {} ------".format(str(i)))
            player_match.pretty_print(player)
            i += 1
    
    # for player_result in get_player_results(driver, config, match_links, config.get('player_in_question')):
    #     player_result.pretty_print(config.get('player_in_question'))


def navigate_to_team_page(table, team_name):
    for row in table.find_elements(By.TAG_NAME, "tr"):
        elements = row.find_elements(By.TAG_NAME, "td")
        text_element = elements[1].find_element(By.TAG_NAME, "h5")
        potential_team_name = text_element.text
        if potential_team_name == team_name:
            row.click()
            return
        
def get_scores(driver, config, link, player_in_question):
    driver.get(link)
    teams_header = driver.find_element(By.XPATH, "//h3 [contains( text(), 'FINAL SCORE')]")
    teams_text = teams_header.find_element(By.XPATH, "..").text
    team_name1 = teams_text.split('\n')[1]
    team_name2 = teams_text.split('\n')[4]

    matches_header = driver.find_element(By.XPATH, "//h3 [contains( text(), 'MATCH BREAKOUT')]")
    driver.implicitly_wait(config.get('wait_times').get('implicit_wait_time'))
    matches_div = matches_header.find_element(By.XPATH, "..")
    driver.implicitly_wait(config.get('wait_times').get('implicit_wait_time'))
    
    individual_matches = matches_div.find_elements(By.XPATH, "./*")[1:6]
    
    player_matches = []
    for individual_match in individual_matches:
        player_match = PlayerMatch(individual_match.text, team_name1, team_name2)
        if player_match.isPlayedBy(player_in_question):
                player_matches.append(player_match)
    


    return player_matches

def get_player_results(driver, config, match_links, player_in_question):
    player_matches = []
    for match_link in match_links:
        player_matches = player_matches + get_scores(driver, config, match_link, player_in_question)

    return player_matches

def get_team_results(driver, config, match_links):
    team_result_matches = {}
    roster = get_roster(driver, config)
    for player in roster:
        team_result_matches[player] = []

    matches = []
    for match_link in match_links:
        matches = matches + get_scores(driver, config, match_link, None)

    for match in matches:
        for player in roster:
            if match.isPlayedBy(player):
                team_result_matches[player].append(match)
    return team_result_matches

def get_roster(driver, config):
    roster_header = driver.find_element(By.XPATH, "//h2 [contains( text(), 'Team Roster')]")
    driver.implicitly_wait(config.get('wait_times').get('implicit_wait_time'))
    roster_div = roster_header.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "a")
    roster = []
    for row in roster_div:
        roster.append(row.text)
    return roster


if __name__ == "__main__":
    main()
