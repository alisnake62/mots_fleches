from datetime import date, timedelta
import datetime
import pandas as pd

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

class DateUtil:

    first_20_minutes_date = date(year=2021, month=1, day=1)

    def get_20_minutes_dates(self):
        start = self.first_20_minutes_date
        end = date.today()
        return [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]