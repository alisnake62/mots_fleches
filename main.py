from func import get_daily_strip, get_full_3mn

import sys
import datetime
import argparse

args = sys.argv

# Créez un objet ArgumentParser
parser = argparse.ArgumentParser(description="Description de votre script")

# Ajoutez des arguments en spécifiant leurs noms et des valeurs par défaut
parser.add_argument('--date_mots_fleches', type=str, default=datetime.datetime.today().strftime("%d%m%Y"), help="date au format ddmmyyyy")
parser.add_argument('--date_comic', type=str, default=datetime.datetime.today().strftime("%d%m%Y"), help="date au format ddmmyyyy")
parser.add_argument('--pic_path', type=str, default='', help="chemin de la photo centrale des mots fleches")
parser.add_argument('--comics', nargs='+', default='', help="list des comics à afficher")

args = parser.parse_args()

for i in args.comics:
    get_daily_strip(args.date_comic, i)

full_3mn = get_full_3mn(args.date_mots_fleches, args.comics, args.pic_path)

with open("3mn.html", "w", encoding="utf-8") as file:
    file.write(full_3mn)    