from func import get_full_3mn, get_central_picture, get_game_id, is_verso_picture, get_nextcloud_id

import sys
import datetime
import os

args = sys.argv

default_date = datetime.datetime.today().strftime("%d%m%Y")
mots_fleches_id = get_game_id(default_date)
nextcloud_id = get_nextcloud_id(default_date)
pic_path = f'central_{nextcloud_id}.png'

# get pictures
img_txt = get_central_picture(nextcloud_id)

if (is_verso_picture(nextcloud_id)):
    with open("html/verso.html", "w") as f:
        f.write(f'<img class="images" src="verso_{nextcloud_id}.png"/>')

print(str(datetime.datetime.now()))

nextcloud_files_only = os.getenv("NEXTCLOUD_FILES_ONLY", "0")

print(f"nextcloud_files_only: {nextcloud_files_only}")

if nextcloud_files_only != '1':

    print("Get Full 3min")
    full_3mn = get_full_3mn(nextcloud_id, mots_fleches_id, pic_path)

    with open("html/index.html", "w", encoding="utf-8") as file:
        file.write(full_3mn)