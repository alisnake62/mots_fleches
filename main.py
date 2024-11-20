from func import get_full_3mn, get_central_picture, get_game_id, is_verso_picture

import sys
import datetime
import os

args = sys.argv

default_date = datetime.datetime.today().strftime("%d%m%Y")
mots_fleches_id = get_game_id(default_date)
pic_path = f'central_{mots_fleches_id}.png'

# get pictures
img_txt = get_central_picture(mots_fleches_id)
is_verso_picture(mots_fleches_id)
# get_verso_picture(mots_fleches_id)

print(str(datetime.datetime.now()))

nextcloud_files_only = os.getenv("NEXTCLOUD_FILES_ONLY", "0")

print(f"nextcloud_files_only: {nextcloud_files_only}")

if nextcloud_files_only != '1':

    print("Get Full 3min")
    full_3mn = get_full_3mn(mots_fleches_id, pic_path)

    with open("html/index.html", "w", encoding="utf-8") as file:
        file.write(full_3mn)