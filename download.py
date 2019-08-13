#!env python3

import requests
from bs4 import BeautifulSoup as bs
import json
import pdb

with open('config.json') as json_data_file:
    config = json.load(json_data_file)

rq = requests.Session()

enter = rq.get(config['url'])
bsenter = bs(enter.text,'html.parser')
form=bsenter.find('form', class_='photo-form')
sessid=form.find('input', attrs={'id':'sessid'})['value']
submit=form.find('input', attrs={'name':'supply_password'})['value']
passname=form.find('input', attrs={'class':'password'})['name']

print("Вход в галерею")

data = {
    'sessid' : sessid,
    passname : config['password'],
    'supply_password': submit
    }
enter2 = rq.post(config['url'], data=data )


bsenter2 = bs(enter2.text,'html.parser')
gal_index = bsenter2.find('ul', attrs={'class' : 'blogs__list'})

for album in gal_index.find_all('li') :
    adate=album.find(attrs={'class':'album-date'}).text
    aurl='http://clevercamp.ru'+album.find(attrs={'class':'blogs__item-link'})['href']
    print(f"Скачиваем всё из {adate}: {aurl}")



