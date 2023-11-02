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

logo_path = '3.png'

options = FirefoxOptions()
options.add_argument("--headless")

horoscope_signs = ["belier", "taureau", "gemeaux", "cancer", "lion", "vierge", "balance", "scorpion", "sagittaire", "capricorne", "verseau", "poissons"]

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

def generate_3mn_mf_from_raw(page_source, force, pic_path=logo_path):
    # Utiliser BeautifulSoup pour analyser le HTML de la page
    soup = BeautifulSoup(page_source, "html.parser")

    soup = replace_images(soup, pic_path)
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
    horoscope = '<div class="horoscope" style="display:grid; grid-template-columns:repeat(3, minmax(0, 1fr))">'
    for sign in horoscope_signs:
        text = get_horoscope_by_sign(sign)
        horoscope +=  f'<div><h3>{sign}</h3>'
        horoscope += f'<p>{text}</p></div>'

    horoscope += '</div>'

    return horoscope

def get_daily_strip(input_date, comic):
    date = datetime.datetime.strptime(input_date, "%d%m%Y") 
    formatted_date = date.strftime("%Y/%m/%d")

    url = f'https://www.gocomics.com/{comic}/{formatted_date}'

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        strip_element = soup.find('picture', class_='item-comic-image')  

        if strip_element:
            image_url = strip_element.find('img')['src']

            # Télécharger l'image
            image_response = requests.get(image_url)

            if image_response.status_code == 200:
                # Enregistrer l'image localement
                with open(f'html/{comic}.png', 'wb') as f:
                    f.write(image_response.content)

                print("Le daily strip a été téléchargé avec succès.")
            else:
                print("Impossible de télécharger l'image du daily strip.")
        else:
            print("Élément du daily strip non trouvé.")
    else:
        print("Impossible de récupérer la page web.")

def get_central_picture(mots_fleches_id):

    nextcloud_password = os.getenv('NEXTCLOUD_ADMIN_PASSWORD', "toto")
    nextcloud_host = "http://monappli.ovh:8889"
    nextcloud_username = "admin"
    nextcloud_url = f"{nextcloud_host}/remote.php/dav/files/{nextcloud_username}"

    # Définissez les en-têtes d'authentification pour Nextcloud
    auth = (nextcloud_username, nextcloud_password)

    extensions = ["png", "jpg", "PNG", "JPG"]

    # Effectuez la demande HTTP pour télécharger le fichier
    try:
        is_downloaded = False
        for file_title in [mots_fleches_id, "default"]:
            for extension in extensions:
                file_name = f"{file_title}.{extension}"
                download_url = f"{nextcloud_url}/3min_photos/{file_name}"
                response = requests.get(download_url, auth=auth)
                if response.status_code == 200:
                    # Enregistrez le contenu du fichier téléchargé localement
                    with open("html/central.png", "wb") as central_picture_file:
                        central_picture_file.write(response.content)
                    is_downloaded = True
                    print(f"Le fichier {file_name} a été téléchargé avec succès.")
                    break
        if not is_downloaded:
            raise Exception()
    except:
        print(f"Échec du téléchargement du fichier")

def get_full_3mn(date_mots_fleches, image_list=[], pic_path= logo_path):
    
    #date
    locale.setlocale(locale.LC_TIME,'')
    date_str = datetime.datetime.strptime(date_mots_fleches, "%d%m%Y").strftime("%d %B %Y")

    #mots fleches
    mots_fleches_id = get_game_id(date_mots_fleches)
    force = get_force(mots_fleches_id)
    mf_raw_html = get_mots_fleches_html_raw(mots_fleches_id)
    mf_3mn = generate_3mn_mf_from_raw(mf_raw_html, force, pic_path)

    # get centra picture
    get_central_picture(mots_fleches_id)

    #horoscope
    horoscope = get_horoscope()

    #comics
    images = ""
    for i in image_list:
        images += f'<img class="images" src="{i}.png"/>'

    # journal complet
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
        <div class="page">
            <em>3mn - Edition du {date_str} - Tirage : 1<em>
            {mf_3mn}
            <em>S'il te reste un peu de temps, n'oublie pas de regarder ton horoscope au verso!</em>
        </div>
        <div class="page">
            <img src={logo_path} height="100px" width="100px">
            {horoscope}
            {images}
        </div>
    </body>
    </html>
    """
