from func import get_daily_strip, get_full_3mn, get_central_picture, get_game_id

import sys
import datetime
import argparse
import os

args = sys.argv

# Créez un objet ArgumentParser
parser = argparse.ArgumentParser(description="Description de votre script")

# Ajoutez des arguments en spécifiant leurs noms et des valeurs par défaut
parser.add_argument('--date_mots_fleches', type=str, default=datetime.datetime.today().strftime("%d%m%Y"), help="date au format ddmmyyyy")
parser.add_argument('--date_comic', type=str, default=datetime.datetime.today().strftime("%d%m%Y"), help="date au format ddmmyyyy")
parser.add_argument('--pic_path', type=str, default='central.png', help="chemin de la photo centrale des mots fleches")
parser.add_argument('--comics', nargs='+', default=['pickles', 'crabgrass'], help="liste des comics à afficher")

args = parser.parse_args()

mots_fleches_id = get_game_id(args.date_mots_fleches)

# get central picture
get_central_picture(mots_fleches_id)

central_picture_only = os.getenv("CENTRAL_PICTURE_ONLY", "0")
if central_picture_only != '1':

    for i in args.comics:
        get_daily_strip(args.date_comic, i)

    full_3mn = get_full_3mn(mots_fleches_id, args.comics, args.pic_path)

    with open("html/index.html", "w", encoding="utf-8") as file:
        file.write(full_3mn)