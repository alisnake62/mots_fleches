from func import get_mots_fleches_html_raw, get_force, generate_3mn_mf_from_raw, get_horoscope, get_full_3mn

import sys
import datetime

args = sys.argv

input_date = None if len(args) == 1 else args[1] # format ddmmyyyy

input_date = datetime.datetime.strptime(input_date, "%d%m%Y") if input_date is not None else datetime.datetime.today()
second_input_date = datetime.datetime.now().strftime("%Y/%m/%d")
formated_date = input_date.strftime("%d%m%Y")
game_id = formated_date[:4] + formated_date[6:]

display_date = input_date.strftime("%d %B %Y")

force = get_force(game_id)

raw_html = get_mots_fleches_html_raw(game_id)

mf_3mn = generate_3mn_mf_from_raw(raw_html, force)

horoscope = get_horoscope(second_input_date)

full_3mn = get_full_3mn(mf_3mn, horoscope)

with open("3mn.html", "w", encoding="utf-8") as file:
    file.write(full_3mn)    