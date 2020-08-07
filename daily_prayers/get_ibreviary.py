##########################################################################################
# Python program to web scrape prayers from the ibreviary.com web site and store
# in ibreviary.json file.
# Program runs on one month selecting year and month as arguments when program is called
#
# e.g. get_ibreviary.py 2020 7
##########################################################################################

import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import calendar

def get_content(session, url):
  page = session.get(url)
  soup = BeautifulSoup(page.text, 'html.parser')
  # content = soup.find('div', {'id' : 'contenuto'})
  return soup.find('div', {'class' : 'inner'})

##########################################################################################
# Start of MAIN
##########################################################################################

url ='http://www.ibreviary.com'
menu = '/m2/letture.php'

parts = ['antiphon_collect', 'prayer_over_offerings', 'antiphon_prayer_after_communion']

links = {'antiphon_collect' : 'http://www.ibreviary.com/m2/letture.php?s=antifona_e_colletta', 
         'prayer_over_offerings' : 'http://www.ibreviary.com/m2/letture.php?s=sulle_offerte',
         'antiphon_prayer_after_communion' : 'http://www.ibreviary.com/m2/letture.php?s=antifona_ed_orazione_dopo_comunione'}



if len(sys.argv) > 1:
  year = int(sys.argv[1])
  month = int(sys.argv[2])
  if month < 1 or month > 12:
    print ("Invalid Month", month)
    sys.exit ('Terminating program run')
  if year < 2020 or year > 2020:
    print ("Invalid Year", year)
    sys.exit ('Terminating program run')

print ('Starting to Scrape Ibreviary Web Site for', year, month, '....')

days = calendar.monthrange(year, month)[1]


ibreviary = {}
with open('ibreviary.json') as json_file: 
    ibreviary = json.load(json_file) 
year = str(year)
month = str(month)

start_day = 1
end_day = calendar.monthrange(int(year), int(month))[1]

if not year in ibreviary: ibreviary[year] = {}
if not month in ibreviary[year]: ibreviary[year][month] = {}

print (year, month, start_day, end_day)
# sys.exit('Normal stop')

session = requests.Session()

for day in range(start_day, end_day+1):

  print ('-----------------------------------------------------------------------------------')
  print (year, month, day)
  if not str(day) in ibreviary[year][month]: 
    print ('Downloading', year, month, day)
    ibreviary[year][month][day] = {}
    page = session.get('http://www.ibreviary.com/m2/opzioni.php')

    form_data = {'lang' : 'en', 'giorno' : str(day), 'mese' : str(month), 'anno' : str(year), 'ok' : 'ok'}

    page = session.post('http://www.ibreviary.com/m2/opzioni.php', form_data)
    ibreviary[year][month][day]['content'] = {}
    # time.sleep(1)

    page = session.get('http://www.ibreviary.com/m2/letture.php')

    for key in links:
      # print (key, links[key])
      content = get_content(session, links[key])
      # if content: content = content.replace('\n','')
      ibreviary[year][month][day]['content'][key] = str(content)
      # print (content)
  # print (soup)

# print (ibreviary.encode('utf-8'))

with open("ibreviary.json", "w") as outfile:  
    json.dump(ibreviary, outfile) 