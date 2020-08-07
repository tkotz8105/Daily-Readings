#!/usr/bin/python

# from urllib.request import urlopen
# from urllib.request import build_opener, HTTPCookieProcessor
import requests

#import the Beautiful soup functions to parse the data returned from the website
from bs4 import BeautifulSoup, NavigableString
import json
import re
import sys

from datetime import datetime as dt
from datetime import timedelta

gospel_acclamation = {'Alleluia' :'', #'Alleluia, Alleluia',
                      'Verse' : 'Praise to You, Lord Jesus Christ, King of Endless Glory!'}

def cvt_dict(header, reading):
    matches = re.findall(r'\n{1,3}', header, re.MULTILINE)

    # if header.startswith('Alleluia'):
    #     header = header.replace('\n','').replace('Alleluia','Alleluia\n')
    if header.startswith('Responsorial'):
        if not 'Psalm' in header: header = header.replace('Responsorial','Responsorial Psalm')
    print (header.encode('utf-8'))
    if matches:
        op = header.split(matches[0])
        type_reading = op[0].strip().replace(' ','_')
    else:
        op = header
        type_reading = op.strip().replace(' ','_')
    reading_dict={}
    # print (op)
    # print (type(op))
    if isinstance(op, list):
        reading_dict['source']=op[1].replace('\n','')
    else:
        reading_dict['source']=''
    # try:
    #     reading_dict['source']=op[1].replace('\n','')
    # except IndexError:
    #     reading_dict['source']=''

    if header.startswith('Reading') or header.startswith('Gospel'):
        op = mrg_reading(reading[0:reading.find('For the readings of the ')-1])
    # elif header.startswith('Alleluia'):
    #     op = mrg_reading(reading)
    #     op.insert(0, gospel_acclamation['Alleluia'])
    #     op.insert(0,'R.')
    #     op.append('R.')      
    #     op.append(gospel_acclamation['Alleluia'])
    elif header.startswith('Verse'):
        op = mrg_reading(reading)
        op.insert(0,gospel_acclamation['Verse'])
        op.insert(0,'R. ')
        op.append('R. ')          
        op.append(gospel_acclamation['Verse'])
    else:
        op = reading.replace('\n\n','\n').replace('  ','').split('\n')
    if op[-1] == '': del op[-1]
    if op[0] == '': op.pop(0)
    reading_dict['narrative']=op
    return type_reading, reading_dict

def mrg_reading(ip):
    end_char =['.','!','?']
    lines = ip.split('\n')
    top = ''
    op = []

    for line in lines:
        if not line.isspace() and len(line)  != 0:
            top = top + ' ' + line.lstrip()
            if line.endswith(tuple(end_char)):
                op.append(top)
                top = ''
    if len(top) != 0: op.append(top)

    return op

def get_site(url):
    # opener = build_opener(HTTPCookieProcessor())
    print (url)
    session = requests.Session()
    # return opener.open(url) 
    return session.get(url).text

def test_multi(page):
    soup = BeautifulSoup(page, features='html.parser')
    division = soup.find('div', {'id' : 'cs_control_3684'})
    links = division.findAll('a', href = True)
    # print (links)
    multiple = False
    if links:
        readings_urls = []
        link_cnt = 0
        for link in links:
            # print (link)
            link_cnt = link_cnt + 1
            readings_urls.append(link['href'])
        if link_cnt > 1: multiple = True
    # print (multiple)
    # if multiple:
    #     print ('Found Multiple Links', readings_urls)
    #     print ('Processing First Link')
    return multiple, readings_urls

def get_dly(date):
    base_url = 'http://www.usccb.org/bible/readings/'    
    url = base_url + date.strftime('%m%d%y') + '.cfm'
    page = get_site(url)

# Test for multiple links on daily page .... if true ... it uses the first link ... need to eventually modify for Diocese preferences
    # multi, urls = test_multi(page)
    multi = False
    if multi:
        print ('Multiple Links on:', date.strftime('%m/%d/%y'))
        print (urls)
    else:
        page = get_site(url)
    return 

def get_readings(date):
    base_url = 'http://www.usccb.org/bible/readings/'    
    url = base_url + date.strftime('%m%d%y') + '.cfm'
    page = get_site(url)

# Test for multiple links on daily page .... if true ... it uses the first link ... need to eventually modify for Diocese preferences
    # multi, urls = test_multi(page)
    multi = False
    if multi:
        page = get_site(urls[2])
    else:
        page = get_site(url)
    return parse_reading(page, date)

def parse_reading(page, date):
    order = ['date', 'description', 'lectionary', 'Reading_1', 'Responsorial_Psalm', 'Reading_2', 'Alleluia', 'Gospel']
    readings_order = ['Reading_1', 'Responsorial_Psalm', 'Reading_2', 'Alleluia', 'Gospel', 'Gospel_(Alt)']

    soup = BeautifulSoup(page, features='html.parser')
    op_dict={}
    op_dict['date'] = date.strftime('%m/%d/%Y')

    readings_block = soup.find('div', {'id' : 'block-usccb-readings-content'})

    lectionary = readings_block.findAll('div', {'class' : 'b-lectionary'})[0]
    op_dict['description'] = lectionary.find('h2').get_text()
    op_dict['lectionary'] = lectionary.find('p').get_text()

    reading_groups = readings_block.findAll('div',{'class' : 'b-verse'})

    for reading_group in reading_groups:
        header_content = reading_group.find('div', {'class' : 'content-header'})
        header = header_content.find('h3', {'class' : 'name'}).get_text() + '\n' + header_content.find('div' , {'class' : 'address'}).get_text()
        if 'Reading II' in header:
            header = header.replace('Reading II', 'Reading 2')
        reading = reading_group.find('div', {'class' : 'content-body'}).get_text('\n')
        reading = re.sub(r'[\xc2\xa0]',"  ",reading)
        for x in ['Or:','or:']: header = header.replace(x, 'Gospel (Alt)', 1)
        type, dict_item = cvt_dict(header, reading)
        op_dict[type] = dict_item

    return op_dict


########################################################################################

def old_parse_reading(page, date):
    # print (soup.encode('utf-8'))
    test_vigil = soup.find('div', {"class" : 'readings'})

    division = test_vigil.find('div', {'id' : 'cs_control_3684'})
    if 'Vigil Mass' in division.get_text():
        links = division.findAll('a', href=True)
        link_vigil = 'http://www.usccb.org' + links[0]['href']
        link_day = 'http://www.usccb.org' + links[1]['href']
        page = urlopen(link_day)
        soup = BeautifulSoup(page, features='html.parser')

    divisions = soup.findAll('div', {"class" : 'readings'})
    division = soup.find('div', {"class" : 'readings'})

    readingTitle = division.find('div', {'id' : 'cs_control_3683'}).get_text('\n')
    op = readingTitle.split('\n')
    op_dict['description'] = op[0]
    op_dict['lectionary'] = op[1]

    reading_groups = soup.findAll('div', {'id' : lambda x: x and x.startswith('cs_control_')})

    for reading_group in reading_groups:
        all_text = reading_group.get_text()

        if 'Reading 1' in all_text or 'At the procession' in all_text:
            if 'At the Mass' in all_text:
                # headers = reading_group.findAll('h4')
                header = reading_group.find('h4').get_text('\n')
                reading = reading_group.findAll('div')[2].get_text('\n')
                reading = re.sub(r'[\xc2\xa0]',"  ",reading)
                matches = re.findall(r'At the Mass {0,3}\n{0,3}\S{0,4} \w{1,4}:[\S| ]{1,50}\n', reading, re.MULTILINE)
                if not matches:
                    header = reading_group.find('h4').get_text('\n')                        
                    type, dict_item = cvt_dict(header, reading)
                    op_dict[type] = dict_item
                else:
                    split_txt = matches[0]
                    header = reading_group.find('h4').get_text('\n')
                    readings = reading.split(split_txt)
                    # for r in readings:
                    #     print (r.encode('utf-8'))
                    type, dict_item = cvt_dict(header, readings[0])
                    op_dict[type] = dict_item
                    header = split_txt.replace('At the Mass','Reading 1')
                    type, dict_item = cvt_dict(header, readings[1])
                    op_dict[type] = dict_item                   
            else:
                header = reading_group.find('h4').get_text('\n')
                if not header.startswith('Read'): header = 'Reading 1\n' + header
                reading = reading_group.findAll('div')[2].get_text('\n')
                type, dict_item = cvt_dict(header, reading)
                op_dict[type] = dict_item
        elif 'Reading 2' in all_text:
            if "Alleluia," in all_text or 'Verse Before the Gospel' in all_text:
                print (reading_group.encode('utf-8'))
                try:
                    # Get Alleluia or Verse Before the Gospel
                    headers = reading_group.findAll('h4')
                    header = headers[1].get_text('\n')
                    reading = reading_group.findAll('div')[3].find('div', {'class':'poetry'}).get_text('\n')
                    print (reading.encode('utf-8'))
                    type, dict_item = cvt_dict(header, reading)
                    op_dict[type] = dict_item
                except (AttributeError, IndexError):
                    print ('Error Found')
                    # Get Alleluia or Verse Before the Gospel
                    try:
                        reading = reading_group.findAll('div')[3].get_text('\n')
                    except (AttributeError, IndexError):
                        reading = reading_group.findAll('div')[2].get_text('\n')
                    print (reading.encode('utf-8'))                 
                    matches = re.findall(r'Verse Before the Gospel {0,3}\n{0,3}\S{0,4} \w{1,4}:[\S| ]{1,50}\n', reading, re.MULTILINE)
                    if not matches: matches = re.findall(r'Alleluia {0,3}\n{0,3}\S{0,4} \w{1,4}:[\S| ]{1,50}\n', reading, re.MULTILINE)
                    if not matches: matches = re.findall(r'Alleluia {0,3}\n{0,3}\S{0,4}.{0,1} {0,4}\d{0,2} {0,4}\w{1,4} {0,4}\w{1,4}:[\S| ]{1,50}\n', reading, re.MULTILINE)
                    if not matches:
                        header = reading_group.find('h4').get_text('\n')                        
                        type, dict_item = cvt_dict(header, reading)
                        op_dict[type] = dict_item
                    else:
                        split_txt = matches[0]
                        header = reading_group.find('h4').get_text('\n')
                        readings = reading.split(split_txt)
                        type, dict_item = cvt_dict(header, readings[0])
                        op_dict[type] = dict_item
                        header = split_txt
                        type, dict_item = cvt_dict(header, readings[1])
                        op_dict[type] = dict_item
                # Get Reading 2
                header = reading_group.find('h4').get_text('\n')
                reading = reading_group.findAll('div')[2].get_text('\n')    
                print (header.encode('utf-8'))
                print (reading.encode('utf-8'))  
                type, dict_item = cvt_dict(header, reading)
                op_dict[type]= dict_item   
            else:
                # headers = reading_group.findAll('h4')
                header = reading_group.find('h4').get_text('\n')
                reading = reading_group.findAll('div')[2].get_text('\n')        
                type, dict_item = cvt_dict(header, reading)
                op_dict[type]= dict_item
        elif 'Responsorial Psalm' in all_text or 'Responsorial' in all_text:
            header = reading_group.find('h4').get_text('\n')
            reading = reading_group.findAll('div')[2].get_text('\n')        
            type, dict_item = cvt_dict(header, reading)
            op_dict[type] = dict_item
        elif "Alleluia" in all_text or 'Verse Before the Gospel' in all_text:
            print ('Found Verse Before the Gospel')
            # headers = reading_group.findAll('h4')
            header = reading_group.find('h4').get_text('\n')
            reading = reading_group.findAll('div')[2].get_text('\n')
            print (header.encode('utf-8'), reading.encode('utf-8'))        
            type, dict_item = cvt_dict(header, reading)
            op_dict[type] = dict_item
        elif "Gospel" in all_text:
            # headers = reading_group.findAll('h4')
            header = reading_group.find('h4').get_text('\n')
            matches = re.findall(r'[O|o]r', header)
            reading = reading_group.findAll('div')[2].get_text('\n').replace(' \n','\n') 
            matches = matches + re.findall(r'[O|o]r {0,3}\n{0,3}\S{0,4} \w{1,4}:[\S| ]{1,50}\n', reading, re.MULTILINE)
            if not matches:
                type, dict_item = cvt_dict(header, reading)
                op_dict[type] = dict_item
            elif len(matches[0]) == 2:
                split_txt = '\n' + matches[0] + '\n'
                headers = header.split(matches[0])
                readings = reading.split(split_txt)
                type, dict_item = cvt_dict(headers[0], readings[0])
                op_dict[type] = dict_item
                type, dict_item = cvt_dict('Gospel (Alt)\n' + re.findall(r'Mt|Mk|Lk|Jn', headers[0])[0] + headers[1], readings[1])
                header = 'Gospel (Alt)'
                op_dict[type] = dict_item           
            else: 
                split_txt = matches[0]
                readings = reading.split(split_txt)
                type, dict_item = cvt_dict(header, readings[0])
                op_dict[type] = dict_item
                header = split_txt
                for x in ['Or','or']: header = header.replace(x, 'Gospel (Alt)', 1)
                type, dict_item = cvt_dict(header, readings[1])
                op_dict[type] = dict_item

        # print (json.dumps(op_dict, sort_keys=True, indent=4))

    return op_dict                
