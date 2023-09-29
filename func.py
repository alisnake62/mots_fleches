from datetime import date, timedelta
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup

horoscope_signs = ["belier", "taureau", "gemeaux", "cancer", "lion", "vierge", "balance", "scorpion", "sagittaire", "capricorne", "verseau", "poissons"]

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def get_force(game_id):
    game_data_request = requests.get(f"https://rcijeux.fr/drupal_game/20minutes/grids/{game_id}.mfj")
    game_data = str(game_data_request.content)
    force = find_between(game_data, "force:\"", "\",\\r")

    return force

def get_mots_fleches_html_raw(game_id):
    # Remplacez l'URL par l'adresse de la page web que vous souhaitez extraire
    url = f"https://www.rcijeux.fr/game/20minutes/mfleches?id={game_id}"
    driver = webdriver.Firefox()

    driver.get(url)

    # Attendre que la page soit complètement chargée (vous pouvez ajuster le délai selon les besoins)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'svg')))

    # Récupérer le HTML de la page
    page_source = driver.page_source

    # Fermer le navigateur
    driver.quit()

    return page_source

def replace_images(soup):
    # Trouvez tous les éléments <image> dans le SVG
    images = soup.find_all("image")

    for i in range(len(images)):
        if(i == 1):
            image = images[i]
            image['xlink:href'] = '3.png'
            

    return soup

def generate_3mn_mf_from_raw(page_source, force):
    # Utiliser BeautifulSoup pour analyser le HTML de la page
    soup = BeautifulSoup(page_source, "html.parser")

    soup = replace_images(soup)
    first_svg = soup.find("svg")

    if first_svg.get("height"):
        del first_svg["height"]

    if first_svg.get("width"):
        del first_svg["width"]

    first_svg["height"] = "97vh"

    # Créez une nouvelle page HTML avec le SVG inclus
    return f"""
    <div class="mots-fleches">
        <text>force {force}</text>
        {first_svg}
    </div>
    """

def get_horoscope_by_sign(sign):
    url = f"https://www.20minutes.fr/horoscope/horoscope-{sign}"

    # Envoyez une requête GET pour récupérer le contenu HTML de la page
    response = requests.get(url)

    # Vérifiez si la requête a réussi (code 200)
    if response.status_code == 200:
        # Récupérez le contenu HTML de la page
        html = response.text
        
        # Créez un objet BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Trouvez le h3 avec la classe "heading-xs@xs" contenant le texte "Humeur"
        h3_element = soup.find('h3', class_='heading-xs@xs', text='Humeur')
        
        # Trouvez le paragraphe voisin du h3
        if h3_element:
            paragraph_element = h3_element.find_next('p', class_='text-m@xs')
            
            # Récupérez le texte du paragraphe
            if paragraph_element:
                texte = paragraph_element.text
                return texte
            else:
                print("Aucun paragraphe trouvé à côté du h3.")
        else:
            print("Aucun h3 trouvé avec le texte 'Humeur'.")
    else:
        print("La requête GET a échoué avec le code de statut :", response.status_code)
    
    return ""

def get_horoscope():
    horoscope = '<div class="horoscope">'
    for sign in horoscope_signs:
        text = get_horoscope_by_sign(sign)
        horoscope +=  f'<h3>{sign}</h3>'
        horoscope += f'<p>{text}</p>'

    horoscope += '</div>'
    return horoscope

def get_full_3mn(mots_fleches, horoscope):
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>3mn</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        {mots_fleches}
        {horoscope}
    </body>
    </html>
    """


class DateUtil:

    first_20_minutes_date = date(year=2021, month=1, day=1)

    def get_20_minutes_dates(self):
        start = self.first_20_minutes_date
        end = date.today()
        return [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]