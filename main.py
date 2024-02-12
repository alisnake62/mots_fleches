from func import get_daily_strip, get_full_3mn, get_central_picture, get_verso_picture, get_game_id

import sys
import datetime
import argparse
import os

args = sys.argv

# Créez un objet ArgumentParser
parser = argparse.ArgumentParser(description="Description de votre script")

default_date = datetime.datetime.today().strftime("%d%m%Y")
default_mots_fleches_id = get_game_id(default_date)

# Ajoutez des arguments en spécifiant leurs noms et des valeurs par défaut
parser.add_argument('--date_mots_fleches', type=str, default=default_date, help="date au format ddmmyyyy")
parser.add_argument('--date_comic', type=str, default=default_date, help="date au format ddmmyyyy")
parser.add_argument('--pic_path', type=str, default=f'central_{default_mots_fleches_id}.png', help="chemin de la photo centrale des mots fleches")
parser.add_argument('--pic_path_verso', type=str, default='verso.png', help="chemin de la photo verso")
parser.add_argument('--comics', nargs='+', default=[], help="liste des comics à afficher")

args = parser.parse_args()

mots_fleches_id = get_game_id(args.date_mots_fleches)

# get pictures
get_central_picture(mots_fleches_id)
get_verso_picture(mots_fleches_id)

central_picture_only = os.getenv("CENTRAL_PICTURE_ONLY", "0")
if central_picture_only != '1':

    for i in args.comics:
        get_daily_strip(args.date_comic, i)

    full_3mn = get_full_3mn(mots_fleches_id, args.pic_path, args.pic_path_verso, args.comics)

    with open("html/index.html", "w", encoding="utf-8") as file:
        file.write(full_3mn)