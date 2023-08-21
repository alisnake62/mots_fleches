from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

import requests
import sys

args = sys.argv

if len(args) == 1:
    gameId = "210823"
else:
    gameId = args[1]

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

title = driver.find_element(By.ID, "game-name")
driver.execute_script(f"document.getElementById('game-name').innerHTML = '{title.text} - Force {force}';")

# driver.close()