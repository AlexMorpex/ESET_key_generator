import requests 
from bs4 import BeautifulSoup
import os 
import logging
import json

handler = logging.StreamHandler()
logger = logging.getLogger('ScrapeLog')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

BASE_URL = 'https://books.toscrape.com/'

if not os.path.exists('./Json_files'):
    logger.debug('Creating directory...')
    os.mkdir('./Json_files')
else:
    logger.debug('Directory already exists ')

response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text,'lxml')
categories = soup.find('ul', class_='nav nav-list').find('li').find('ul').find_all('li')

categories_dict = {}
for el in categories:
    category = el.find('a').get_text(strip=True)
    link = el.find('a').get('href').replace('/index.html','')
    categories_dict[category]=BASE_URL+link

if not os.path.exists('./Json_files/Categories.json'):
    logger.debug("Creating 'Categories.json'")
    with open('./Json_files/Categories.json','x')as f:   
        json.dump(categories_dict,f,indent=4)
else:
    logger.debug("Writing 'Categories.json'")
    with open('./Json_files/Categories.json','w')as f:   
        json.dump(categories_dict,f,indent=4)


full_dict = {}
for category in categories_dict:
    logger.debug(f"{'='*10}{'\n'}{category}{'\n'}{'='*10}")
    full_dict[category] = {}

    response = requests.get(categories_dict[category])
    soup = BeautifulSoup(response.text,'lxml')
    for el in soup.find_all('li',class_='col-xs-6 col-sm-4 col-md-3 col-lg-3'):
        link = el.find('h3').find('a').get('href')
        name = el.find('h3').find('a').get('title')
        logger.debug(f"{'-'*10}{'\n'}{name}{'\n'}{'-'*10}")
        full_dict[category][name] = categories_dict[category]+'/'+link




if not os.path.exists('./Json_files/Books.json'):
    logger.debug("Creating 'Books.json'")
    with open('./Json_files/Books.json','x')as f:   
        json.dump(full_dict,f,indent=4)
else:
    logger.debug("Writing 'Books.json'")
    with open('./Json_files/Books.json','w')as f:   
        json.dump(full_dict,f,indent=4)

