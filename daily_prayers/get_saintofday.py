#!/usr/bin/python3

from xvfbwrapper import Xvfb
from pyvirtualdisplay import Display
from selenium import webdriver

# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
# from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
#import the Beautiful soup functions to parse the data returned from the website
from bs4 import BeautifulSoup
import json
import time
import re

from datetime import datetime as dt

def get_page(url):
    path_to_chromedriver = '/usr/bin/chromedriver' # change path as needed
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')

    vdisplay = Xvfb()
    vdisplay.start()
    
    display = Display(visible=0, size=(1024, 768))
    display.start()

    browser = webdriver.Chrome(executable_path = path_to_chromedriver,
    service_args=["--verbose", "--log-path=/tmp/CHROMIUM_LOG"],
    options=chrome_options)
    
    browser.get(url)
    time.sleep(2)
    page = browser.page_source

    browser.close()
    display.stop()
    vdisplay.stop()

    return page

date_today = dt.today()
strdate = date_today.strftime('%Y-%m-%d')

# strdate = '2019-09-17'
home_dir = '/home/apps/'

# Get & scrape main saint of day page to get link to saint information
url = 'https://www.franciscanmedia.org/sod-calendar'
page = get_page(url)
soup = BeautifulSoup(page, features='html.parser')

for td in soup.find_all('td', {'class':'sotd_calendar--day', 'rel': True}):
    # print (td['rel'], strdate)
    if td['rel'] == strdate:
        # print ('........................', td['rel'])
        href = td.find('a', {'class' : 'sotd_calendar--link'})['href']
        # print (href)

# Using saint link, get & scrape saint page and populate dictionary 
page2 = get_page(href)
soup2 = BeautifulSoup(page2, features='html.parser')
section = soup2.find('div', {'class' : 'entry-content'})

# populate dictionary op_dict
op_dict = {}
strdate = date_today.strftime('%m/%d/%Y')
op_dict[strdate] = {} 
op_dict[strdate]['img_link'] = section.find('img')['src']
op_dict[strdate]['saint'] = section.find('h1').get_text()
op_dict[strdate]['description'] = section.find('h2').get_text()
try:
    op_dict[strdate]['lifetime'] = section.find('h4').get_text()
except AttributeError:
    pass

op_dict[strdate]['story_title'] = section.find('h3').get_text()
# print (op_dict.encode('utf-8'))

# Find all pargaraphs and look for 2nd h3 tag to determine whether narrative or reflection
paragraphs = section.findAll('p')
narrative = []
reflection = []
patron = []
h3 = 0
reflection_test = False
patron_test = False

p = section.find('p')
# narrative.append(p.get_text())
while not reflection_test:
    # for paragraph in section.findAll('p'):
    p = p.find_next_sibling()
    if p.name == 'p':
        narrative.append(p.get_text())
    elif p.name == 'h3' and p.get_text() == 'Reflection':
        reflection_test = True

if section.find('h3', text="Reflection"):
    p = section.find('h3', text="Reflection").findNext('p')
    # print ('*****************************   ', p)
    # reflection.append(p)
    reflection.append(p.get_text())
    while not patron_test:
        p = p.find_next_sibling()
        # print ('*****************************   ', p)
        if p.name == 'p':
            # p = p.next_sibling
            reflection.append(p.get_text())
        else:
            patron_test = True
            
        # for reflection.append(section.find(text="Reflection").findNext('p').get_text())

if section.find('h3', text=re.compile(r'Patron Saint')):
    patron = (section.find(text=re.compile(r'Patron Saint')).findNext('p').get_text().split('\n'))

while not reflection_test:
    for paragraph in section.findAll('p'):
        sibling = paragraph.previous_sibling.previous_sibling
        if sibling.name == 'h3' and sibling.get_text() == 'Reflection':
            reflection_test = True
        else:
            narrative.append(paragraph.get_text())
            # print (paragraph.get_text())

op_dict[strdate]['narrative'] = narrative
op_dict[strdate]['reflection'] = reflection
op_dict[strdate]['patron'] = patron

# print (op_dict)

print (json.dumps(op_dict, sort_keys=True, indent=4))

with open(home_dir + 'todays_saint.json', 'w') as op_file:
    json.dump(op_dict, op_file)
