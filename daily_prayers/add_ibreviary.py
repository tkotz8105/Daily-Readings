import json
from bs4 import BeautifulSoup

home_dir = '/home/apps/'

def get_ibreviary(year, month, day):

  headers = ['Prayer after Communion', 'Antiphon', 'Collect', 'Prayer over the Offerings']

  parts = ['antiphon_collect', 'prayer_over_offerings', 'antiphon_prayer_after_communion']

  # Opening JSON file 
  with open(home_dir+'ibreviary.json') as json_file: 
      ibreviary = json.load(json_file) 

  # content = ibreviary[year][month][day]['content']
  content = ibreviary[str(year)][str(month)][str(day)]['content']  

  prayers = {}
  cntr = 0
  # prayers['prayers'] = []
  for part in parts:
    html = content[part].replace('<br/>','\n')
    # print (key, content[key])
    soup = BeautifulSoup(html,'html.parser')
    header = soup.find('h1')
    # print (header.text)
    spans = soup.findAll('span')
    paras = soup.findAll('p')
    for para in paras:
      if para.find('span'):
        header = para.find('span').text
        if header in headers:
          cntr = cntr + 1
          print ('------------', para.find('span').text)
          # prayers[cntr]= {}
          if header == 'Antiphon':
            if cntr == 1:
              current_header = header + "_1"
            else:
              current_header = header + "_2"
          else:
            current_header = header.replace(' ','_')
          prayers[current_header] = {}
          prayers[current_header]['source'] = ''
          prayers[current_header]['narrative'] = []
        else:
          print (para.text.encode('utf-8'))
          if not 'Antiphon and ' in header: prayers[current_header]['narrative'] = prep_text(para.text)
      elif 'Menu' in para.text:
        pass        
      else:
        # print (para)
        prayers[current_header]['narrative'] = prep_text(para.text)

  for key in prayers:
    readings[key] = prayers[key]

  for key in readings:
    print (key) 

  return readings

def prep_text(para):
  data = para
  if 'The Gloria in excelsis' in data:
    return data[0:data.find('The Gloria in excelsis')].split('\n')
  elif 'The following Solemn Blessing may be used:' in data:
    return data[0:data.find('The following Solemn Blessing may be used:')].split('\n')
  else:
    return data.split('\n')

###################################################################################################
# Start of Main
###################################################################################################


json_files = ['todays_reading.json', 'nextday_reading.json', 'sundays_reading.json']
files = []

for json_file in json_files:
  files.append(home_dir + json_file)

for file in files:
  with open(file) as json_file: 
      readings = json.load(json_file) 

  date = readings['date'].split('/')
  # "date": "07/05/2020",
  year = date[2]
  month = date[0].lstrip('0')
  day = date[1].lstrip('0')

  print (year, month, day)

  readings_op = get_ibreviary(year, month, day)

  with open(file, "w") as outfile:  
      json.dump(readings_op, outfile) 