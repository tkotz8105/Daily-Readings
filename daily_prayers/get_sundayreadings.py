#!/usr/bin/python

from urllib.request import urlopen
#import the Beautiful soup functions to parse the data returned from the website
from bs4 import BeautifulSoup
import json

from datetime import datetime as dt
from datetime import timedelta

from get_readings import get_readings
from get_readings import cvt_dict

home_dir = '/home/tkotz/apps/tkotz.us/'

date_today = dt.today()
day_of_week = date_today.weekday()

sunday = date_today + timedelta( (6-date_today.weekday()) % 7) 
print (sunday)
op_dict = get_readings(sunday)

print (json.dumps(op_dict, sort_keys=True, indent=4))

with open(home_dir + 'sundays_reading.json', 'w') as op_file:
    json.dump(op_dict, op_file)
