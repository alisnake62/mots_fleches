from func import get_full_3mn, get_central_picture, get_verso_picture, get_game_id

import sys
import datetime

args = sys.argv

default_date = datetime.datetime.today().strftime("%d%m%Y")
mots_fleches_id = get_game_id(default_date)
pic_path = f'central_{mots_fleches_id}.png'

# get pictures
img_txt = get_central_picture(mots_fleches_id)
get_verso_picture(mots_fleches_id)

full_3mn = get_full_3mn(mots_fleches_id, pic_path, img_txt)

with open("html/index.html", "w", encoding="utf-8") as file:
    file.write(full_3mn)