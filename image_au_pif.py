import datetime
from func import get_game_id, teleprendre_national_geographic, generer_nombre_unique

index = generer_nombre_unique()

default_date = datetime.datetime.today().strftime("%d%m%Y")
mots_fleches_id = get_game_id(default_date)
pic_path = f'central_{mots_fleches_id}'

teleprendre_national_geographic(index, pic_path, mots_fleches_id)