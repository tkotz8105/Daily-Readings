#!/usr/bin/python

from urllib.request import urlopen
#import the Beautiful soup functions to parse the data returned from the website
from bs4 import BeautifulSoup
import json

from datetime import datetime as dt
from datetime import timedelta

from get_readings import get_readings
from get_readings import cvt_dict

days = ['today', 'tomorrow','sunday']
# days = ['5/22/2020']

opfile = {'today' : 'todays_reading.json',
          'tomorrow' : 'nextday_reading.json',
          'sunday' : 'sundays_reading.json'}

home_dir = '/home/apps/'

date_today = dt.today()
day_of_week = date_today.weekday()

for day in days:
    if day == 'today':
        get_date = date_today
    elif day == 'tomorrow':
        get_date = date_today + timedelta(hours=24)
    elif day == 'sunday':
        if date_today.weekday() == 6:
            get_date = date_today + timedelta(7)
        else:
            get_date = date_today + timedelta((6-date_today.weekday()) % 7) 
    else:
        # try:
        get_date = dt.strptime(day, '%m/%d/%Y')
        opfile[day] = get_date.strftime('%Y%m%d') + '_reading.json'
        # except:
        #     print ('Error in date conversion')

    op_dict = get_readings(get_date)

    print (json.dumps(op_dict, sort_keys=True, indent=4))

    with open(home_dir + opfile[day], 'w', encoding='utf8', errors="ignore") as op_file:
        json.dump(op_dict, op_file)

print ('Job Complete')
