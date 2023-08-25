from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

import requests
import sys
import datetime

args = sys.argv

input_date = None if len(args) == 1 else args[1]

input_date = datetime.datetime.strptime(input_date, "%d%m%Y") if input_date is not None else datetime.datetime.today()

formated_date = input_date.strftime("%d%m%Y")
game_id = formated_date[:4] + formated_date[6:]

display_date = input_date.strftime("%d %B %Y")

options = Options()
options.headless = False

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

game_data_dequest = requests.get(f"https://rcijeux.fr/drupal_game/20minutes/grids/{game_id}.mfj")
game_data = str(game_data_dequest.content)
force = find_between(game_data, "force:\"", "\",\\r")

driver = Firefox(options=options)
driver.get(f"https://rcijeux.fr/game/20minutes/mfleches?id={game_id}")

title_element = driver.find_element(By.ID, "game-name")
driver.execute_script(f"document.getElementById('game-name').innerHTML = '{display_date} - Force {force}';")

# driver.close()