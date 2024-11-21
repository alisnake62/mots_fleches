from datetime import date
import datetime
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import locale
import os
from openai import OpenAI
import traceback
import sys
import json
import random

logo_path = 'static/3.png'

options = FirefoxOptions()
options.add_argument("--headless")

horoscope_signs = ["belier", "taureau", "gemeaux", "cancer", "lion", "vierge", "balance", "scorpion", "sagittaire", "capricorne", "verseau", "poissons"]

nextcloud_password = os.getenv('NEXTCLOUD_ADMIN_PASSWORD', "toto")
nextcloud_host = "http://monappli.ovh:8889"
nextcloud_username = "admin"
nextcloud_url = f"{nextcloud_host}/remote.php/dav/files/{nextcloud_username}"

# Définissez les en-têtes d'authentification pour Nextcloud
auth = (nextcloud_username, nextcloud_password)

def generer_nombre_unique():
    # Charger l'array depuis le fichier Nextcloud
    fichier_nextcloud = f"{nextcloud_url}/3min_photos/ng_index.json"

    # Effectuer une requête HTTP pour obtenir les données actuelles
    response = requests.get(fichier_nextcloud, auth=auth)

    # Vérifier si la requête a réussi (code de statut 200)
    if response.status_code == 200:
        # Charger les données depuis la réponse JSON
        donnees = response.json()
    else:
        print(response)
        print("Erreur lors de la récupération des données depuis Nextcloud.")
        return None

    if len(donnees) == 1294:
        return None

    # Générer un nombre aléatoire unique entre 1 et 1200
    nombre_aleatoire = random.randint(1, 1294)
    while nombre_aleatoire in donnees:
        nombre_aleatoire = random.randint(1, 1294)

    # Ajouter le nombre aléatoire à l'array
    donnees.append(nombre_aleatoire)

    # Enregistrer les données mises à jour dans le fichier Nextcloud
    response = requests.put(fichier_nextcloud, json=donnees, auth=auth)

    # Vérifier si la requête de mise à jour a réussi
    if response.status_code == 204:
        print("Données mises à jour avec succès sur Nextcloud.")
        return nombre_aleatoire
    else:
        print(response)
        print("Erreur lors de la mise à jour des données sur Nextcloud.")
        return None

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def get_game_id(input_date):
    input_date_mots_fleches = datetime.datetime.strptime(input_date, "%d%m%Y") 
    formated_date_mots_fleches = input_date_mots_fleches.strftime("%d%m%Y")
    return formated_date_mots_fleches[:4] + formated_date_mots_fleches[6:]


def get_force(game_id):
    game_data_request = requests.get(f"https://rcijeux.fr/drupal_game/20minutes/grids/{game_id}.mfj")
    game_data = str(game_data_request.content)
    force = find_between(game_data, "force:\"", "\",\\r")

    return force

def get_mots_fleches_html_raw(game_id):
    # Remplacez l'URL par l'adresse de la page web que vous souhaitez extraire
    
    url = f"https://www.rcijeux.fr/game/20minutes/mfleches?id={game_id}"
    driver = webdriver.Firefox(options=options)

    driver.get(url)

    # Attendre que la page soit complètement chargée (vous pouvez ajuster le délai selon les besoins)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'svg')))

    # Récupérer le HTML de la page
    page_source = driver.page_source

    # Fermer le navigateur
    driver.quit()

    return page_source

def replace_images(soup, image1=logo_path, image2=logo_path):
    # Trouvez tous les éléments <image> dans le SVG
    images = soup.find_all("image")

    for i in range(len(images)):
        if(i == 0):
            image = images[i]
            image['xlink:href'] = image1

        if(i == 1):
            image = images[i]
            image['xlink:href'] = image2


    return soup

def generate_3mn_mf_from_raw(page_source, force, pic_path):
    # Utiliser BeautifulSoup pour analyser le HTML de la page
    soup = BeautifulSoup(page_source, "html.parser")

    soup = replace_images(soup, pic_path, logo_path)
    first_svg = soup.find("svg")

    if first_svg.get("height"):
        del first_svg["height"]

    if first_svg.get("width"):
        del first_svg["width"]


    # Créez une nouvelle page HTML avec le SVG inclus
    return f"""
    <div>
        <text>force {force}</text>
        {first_svg}
        <br/><br/>
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
        
        h2_element = soup.find('h3', class_='heading-xs@xs', text='Amour')

        # Trouvez le paragraphe voisin du h3
        if h2_element:
            paragraph_element = h2_element.find_next('p')
            
            # Récupérez le texte du paragraphe
            if paragraph_element:
                texte = paragraph_element.text
                return texte
            else:
                print("Aucun paragraphe trouvé à côté du h2.")
        else:
            print("Aucun h2 trouvé avec le texte 'Amour'.")
    else:
        print("La requête GET a échoué avec le code de statut :", response.status_code)
    
    return ""

class IAClient:

    def __init__(self) -> None:
        api_key = os.getenv('OPEN_API_KEY')
        self.client = OpenAI(api_key=api_key)

    def transform_horoscope_text(self, text):
        with open("horoscope_ia_prompt.txt", 'r') as file:
            prompt = file.read()
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
        )

        return completion.choices[0].message.content

    def get_gorafi_text(self):
        with open("gorafi_ia_prompt.txt", 'r') as file:
            prompt = file.read()
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
            ]
        )

        return completion.choices[0].message.content

def get_horoscope():
    print(f"Téléchargement de l'horoscope")
    horoscope = '<div class="horoscope" style="display:grid; grid-template-columns:repeat(3, minmax(0, 1fr))">'

    ia = IAClient()

    for sign in horoscope_signs:

        text = get_horoscope_by_sign(sign)
        try:
            text = ia.transform_horoscope_text(text)
        except Exception as err:
            print(traceback.format_exc(), file = sys.stderr )
        horoscope +=  f'<div><h3>{sign}</h3>'
        horoscope += f'<p>{text}</p></div>'

    horoscope += '</div>'

    return horoscope

def get_gorafi():
    print(f"Téléchargement du Gorafi")
    ia = IAClient()
    return ia.get_gorafi_text()

def teleprendre_image(date, folder, filename):
    extensions = ["png", "jpg", "PNG", "JPG"]

    # Effectuez la demande HTTP pour télécharger le fichier
    is_downloaded = False
    file_title = date
    for extension in extensions:
        file_name = f"{file_title}.{extension}"
        download_url = f"{nextcloud_url}/{folder}/{file_name}"

        print(f"Essai de téléprendre '{file_name}'")
        response = requests.get(download_url, auth=auth)
        if response.status_code == 200:
        # Enregistrez le contenu du fichier téléchargé localement
            with open(f"html/{filename}.png", "wb") as f:
                f.write(response.content)
            is_downloaded = True
            print(f"Le fichier {file_name} a été téléchargé avec succès.")
            break
        if is_downloaded:
                break
    if not is_downloaded:
        print('Échec du téléchargement du fichier')
        raise Exception("error")

def get_central_picture(mots_fleches_id):
    try:
        teleprendre_image(mots_fleches_id, "3min_photos", f"central_{mots_fleches_id}")
    except:
        teleprendre_image("default", "3min_photos", f"central_{mots_fleches_id}")

def is_verso_picture(mots_fleches_id):
    try:
        teleprendre_image(mots_fleches_id, "3min_photos_verso", f"verso_{mots_fleches_id}")
        return True
    except:
        print('no verso picture bro')
        return False


def get_full_3mn(mots_fleches_id, pic_path):

    #date
    locale.setlocale(locale.LC_TIME,'')
    date_str = datetime.datetime.strptime(mots_fleches_id, "%d%m%y").strftime("%d %B %Y")

    #mots fleches
    force = get_force(mots_fleches_id)
    mf_raw_html = get_mots_fleches_html_raw(mots_fleches_id)
    mf_3mn = generate_3mn_mf_from_raw(mf_raw_html, force, pic_path)

    #horoscope
    horoscope = get_horoscope()

    verso = ''
    #verso pic or gorafi, that is the question
    if (is_verso_picture(mots_fleches_id)):
        with open("html/verso.html", "w") as f:
            f.write(f'<img class="images" src="verso_{mots_fleches_id}.png"/>')
    else:
        verso = get_gorafi()
        with open("html/verso.html", "w") as f:
            f.write(verso)

    # journal complet
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>3mn</title>
        <link rel="stylesheet" href="static/style.css">
        <script src="https://unpkg.com/htmlincludejs"></script>
    </head>
    <body>
        <div class="page">
            <em>3mn - Edition du {date_str} - Tirage : 1<em>
            {mf_3mn}
            <em>S'il te reste un peu de temps, n'oublie pas de regarder ton horoscope au verso!</em>
        </div>
        <div class="page">
            <img src={logo_path} height="100px" width="100px">
            {horoscope}
            <h2>
            Breaking News
            </h2>
            <p>
                <include src="./verso.html"></include>
            </p>
        </div>
    </body>
    </html>
    """
