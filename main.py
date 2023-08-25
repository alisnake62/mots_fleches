from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

import requests
import sys
import datetime

args = sys.argv

if len(args) == 1:
    gameId = "250823"
else:
    gameId = args[1]

formated_date = gameId[:4] + '20' + gameId[4:]
date_str = datetime.datetime.strptime(formated_date, "%d%m%Y").strftime("%d %B %Y")

options = Options()
options.headless = False

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

gameDataRequest = requests.get(f"https://rcijeux.fr/drupal_game/20minutes/grids/{gameId}.mfj")
gameData = str(gameDataRequest.content)
force = find_between(gameData, "force:\"", "\",\\r")

driver = Firefox(options=options)
driver.get(f"https://rcijeux.fr/game/20minutes/mfleches?id={gameId}")

title_element = driver.find_element(By.ID, "game-name")
driver.execute_script(f"document.getElementById('game-name').innerHTML = '{date_str} - Force {force}';")

# driver.close()