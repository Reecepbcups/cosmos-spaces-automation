# Helper Class

import time, datetime

# Functions
def get_epoch_time_seconds():
    return int(time.time())

def convert_date_to_human_readable(ISO8861_date: str) -> str: # https://strftime.org/
    return datetime.datetime.strptime(ISO8861_date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d %b %Y %H:%M UTC')    


