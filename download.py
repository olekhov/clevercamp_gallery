#!env python3

import requests
from bs4 import BeautifulSoup as bs
import json
import pdb
import os
from tqdm import tqdm

class FileCollection():
    """ Коллекция файлов """
    def __init__(self,dlfolder):
        self.dlfiles={}
        self.dlfolder=dlfolder
        self.site="http://clevercamp.ru"

        if not os.path.isdir(self.dlfolder):
            print(f"Каталога [{self.dlfolder}] для скачивания не существует. создаём")
            os.mkdir(self.dlfolder)

        if os.path.isfile(self.dlfolder+"/filelist.txt"):
            print("Есть файл со списком уже скачанного")
            with open(self.dlfolder+"/filelist.txt","r") as f:
                url,filename=f.read()
                self.dlfiles[url]=filename
        else:
            print("Коллекция пустая")
        pass

    def SaveCache(self):
        with open(self.dlfolder+"/filelist.txt","w") as f:
            for k,v in self.dlfiles.items():
                f.write(f"{k} {v}\n")


    def DownloadFile(self, u, fn, desc):
        #pdb.set_trace()
        url=self.site+u
        r=requests.head(url)
        sz=int(r.headers.get('content-length', None))
        filename=self.dlfolder+'/'+fn
        if os.path.isfile(filename):
            s=os.stat(filename)
            if s.st_size == sz:
                print(f"{desc} уже загружен")
                return
            else:
                print(f"{desc} есть, но размер не тот. скачиваем заново")
        r=requests.get(url,stream=True)
        pbar=tqdm(r.iter_content(chunk_size=4096), desc=desc, unit="B", unit_scale=1, unit_divisor=4096,total=sz)
        with open(filename,"wb") as f:
            for data in pbar:
                f.write(data)
                pbar.update(len(data))
        pbar.close()
        r.close()
        self.dlfiles[url]=filename
        self.SaveCache()


with open('config.json') as json_data_file:
    config = json.load(json_data_file)

fc = FileCollection(config['dlfolder'])
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
    photo_array_url=f"{aurl}/?UCID=bxph_list_0&sessid={sessid}&return_array=Y&PAGEN_2=1"
    photo_array=rq.get(photo_array_url)
    # выкинуть из текста "window.bxphres = "
    pa= bs(photo_array.text,'html.parser').text[17:].replace("'",'"')
    pa_list=pa.split('\n')
    total = int(pa_list[4][15:-2])
    pages = int(pa_list[5][14:-1])
#    pdb.set_trace()
    print(f"Всего {total} фото на {pages} страницах")
    for p in range(1,pages+1):
        photo_array_url=f"{aurl}/?UCID=bxph_list_0&sessid={sessid}&return_array=Y&PAGEN_2={p}"
        photo_array=rq.get(photo_array_url)
        pa= bs(photo_array.text,'html.parser').text[17:].replace("'",'"')
        pa_list=pa.split('\n')
        pajs = json.loads(pa_list[1][9:-1])
        #pdb.set_trace()
        for k,v in pajs.items():
            print(f"Скачиваем {v['src']} в {v['title']} index: {v['index']} добавлено: {v['date']}")
            idx=int(v['index'])
            if not os.path.isdir(config['dlfolder']+'/'+v['album_name']):
                print(f"Альбома {v['album_name']} не существует. создаём")
                os.mkdir(config['dlfolder']+'/'+v['album_name'])
            fn=f"{v['album_name']}/{idx:03}-{v['title']}"
            print(f"Будет сохранён в {fn}")
            fc.DownloadFile(v['src'],fn,v['title'])
            #fn=


            #pdb.set_trace()




    # {aurl}/?UCID=bxph_list_0&sessid={sessid}&return_array=Y&PAGEN_2={page}'



