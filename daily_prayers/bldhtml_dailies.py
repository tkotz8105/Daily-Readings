#!/usr/bin/python

import json
from datetime import datetime as dt

def single_HTML(ip, tag, classes):
    if classes == '':
        op = '<' + tag + '>' + ip + '</' + tag + '>'
    else:
        op = '<' + tag + ' class="' + classes + '">' + ip + '</' + tag + '>'
    return op

div = 'div'

h1 = 'h1'
h2 = 'h2'
h3 = 'h3'
h4 = 'h4'
p = 'p'
br = 'br'

textleft = 'text-left'
textcenter = 'text-center'
textright = 'text-right'



saint_order = ['description', 'saint', 'lifetime', 'story_title', 'narrative', 'reflection', 'patron']

def bld_readings(op_dict):

    readings_order = ['Antiphon_1', 'Collect', 'Reading_1', 'Responsorial_Psalm', 'Reading_2', 'Alleluia',
                      'Verse_Before_the_Gospel', 'Gospel', 'Gospel_(Alt)', 'Prayer_over_the_Offerings', 
                      'Antiphon_2', 'Prayer_after_Communion']
    headers = {'Reading_1' : 'Reading 1', 'Responsorial_Psalm' : 'Responsorial Psalm',
               'Reading_2' : 'Reading 2', 'Alleluia' : 'Alleluia', 'Gospel' : 'Gospel',
               'Gospel_(Alt)' : 'Gospel (Alternate Reading)',
               'Verse_Before_the_Gospel': 'Verse Before the Gospel',
               'Prayer_after_Communion' : 'Prayer after Communion',
               'Antiphon_1' : 'Antiphon',
               'Collect' : 'Collect', 
               'Prayer_over_the_Offerings' : 'Prayer over the Offerings'}


    strReadings = '<html><head></head><body>'

    strReadings = strReadings + '<div class="text-left">' + single_HTML(op_dict['description'], h3, textcenter)
    # print (strReadings)
    strReadings = strReadings +  single_HTML(op_dict['date'], h3, textcenter)
    # strReadings = strReadings + create_HTML(op_dict['lectionary'], h1)

    for z in readings_order:
        try:
            # lenReading = len(op_dict[z]['narrative'])
            # strReadings = strReadings + ('<tr><td class="text-left">' + headers[z] + '</td' + 
            #                              '<td class="text-right">' + op_dict[z]['source'] + '</td></tr>')
            strReadings = strReadings + '<br>' + ('<h4 class="text-left text-capitalize">' + headers[z] + ':  ' + 
                            '<span class="text-uppercase float-right">' + op_dict[z]['source'] + '</span></h4>')
            refrain = False
            for y in range(len(op_dict[z]['narrative'])):
                text = op_dict[z]['narrative'][y]
                # print (refrain, text.encode('utf-8)'))
                if text.startswith('R.') or text.startswith('R.('):
                    strReadings = strReadings + '<strong>' + text + '</strong>'
                    refrain = True
                elif refrain:
                    strReadings = strReadings + '<strong>' + text + '</strong><br>'
                    refrain = False
                else:
                    strReadings = strReadings + text + '<br>'
                    # strReadings = strReadings + op_dict[z]['narrative'][y] + '<br>'
            strReadings = strReadings + '<hr class="style13">'
        except KeyError:
            pass
        # except:
        #     print ('error in code')

    
    return strReadings + '</div></body></html>'

    
def bld_saintofday(op_dict):       # Saint of the Day

    strReadings = '<html><head></head><body>'

    strReadings = strReadings + '<div class="text-left">' + single_HTML(op_dict['description'], h3, textcenter)
    # print (strReadings)
    strReadings = strReadings +  single_HTML(op_dict['saint'], h3, textcenter)

    try:
        strReadings = strReadings +  single_HTML(op_dict['lifetime'], h4, textcenter)
    except KeyError:
        pass

    strReadings = strReadings + '<br>' + single_HTML(op_dict['story_title'], h4, textcenter)

    for para in op_dict['narrative']:
        strReadings = strReadings + single_HTML(para, p, textleft)

    strReadings = strReadings + '<br>' + single_HTML('Reflection', h4, textleft)
    for para in op_dict['reflection']:
        strReadings = strReadings + single_HTML(para, p, textleft)

    if len(op_dict['patron'])>0:
        strReadings = strReadings + '<br>' + single_HTML('Patron Saint of', h4, textleft) + '<p>'
        for patron in op_dict['patron']:
            strReadings = strReadings + patron + ', '
        strReadings = strReadings[:-2] + '</p>'

    return strReadings + '<hr></div></body></html>'


#####################################################

php_dir = '/var/www/html/'
home_dir = '/home/apps/'

ipfile = home_dir + 'todays_reading.json'
with open(ipfile) as json_file:
    ip_dict = json.load(json_file)
readings = bld_readings(ip_dict)
# print (readings.encode('utf-8'))
with open(php_dir + 'todays_reading.php', 'w', encoding='utf8', errors="ignore") as html_file:
    html_file.write(readings)

date_today = dt.today()
strdate = date_today.strftime('%m/%d/%Y')
print (strdate+': '+' Saving Daily Readings & Saint of the Day to html')
ipfile = home_dir + 'todays_saint.json'
with open(home_dir + 'todays_saint.json') as json_file:
    dict = json.load(json_file)
ip_dict = dict[strdate]
readings = bld_saintofday(ip_dict)
# print (readings.encode('utf-8'))
with open(php_dir + 'todays_saint.php', 'w',encoding='utf8', errors="ignore") as html_file:
    html_file.write(readings)

ipfile = home_dir + 'nextday_reading.json'
with open(ipfile) as json_file:
    ip_dict = json.load(json_file)
readings = bld_readings(ip_dict)
# print (readings.encode('utf-8'))
with open(php_dir + 'nextday_reading.php', 'w',encoding='utf8', errors="ignore") as html_file:
    html_file.write(readings)

    ipfile = home_dir + 'sundays_reading.json'
with open(ipfile) as json_file:
    ip_dict = json.load(json_file)
readings = bld_readings(ip_dict)
# print (readings.encode('utf-8'))
with open(php_dir + 'sundays_reading.php', 'w',encoding='utf8', errors="ignore") as html_file:
    html_file.write(readings)
print ("Job Completed")
