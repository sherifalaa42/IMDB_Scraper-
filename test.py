from email.header import Header
from wsgiref.headers import Headers
import requests
from bs4 import BeautifulSoup
import sqlite3
import numpy as np

category_list = []
casting_list = []
creators_list = []
details_t = []
production_comp = []
'''
IMDB Scraper 

Scrapes Item's Data for full Category of IMDB 
(Comedy is used)

Scrapes item's
[Name,Rating,Type(Film,Series),
About,Img,Vid,Release Date,
Categories,Casting,Creators,
Production Companies,Time,
(Episodes,Seasons)if Series]

'''

try:
        page = requests.get('https://www.imdb.com/search/keyword/?keywords=comedian&ref_=fn_al_kw_1')
        soup = BeautifulSoup(page.content,'html.parser')

        comedy_page_items = soup.find_all('div',class_='lister-item mode-detail')
        for film in comedy_page_items :
                        
                film_title = film.find('a').get('href')
                film_url_full = 'https://www.imdb.com' + film_title
                film_page_request = requests.get(film_url_full)
                film_soup = BeautifulSoup(film_page_request.content,'html.parser')

                name = film_soup.find('h1',class_='sc-b73cd867-0 eKrKux').get_text()
                rating = film_soup.find('span',class_='sc-7ab21ed2-1 jGRxWM').get_text()
                
                about = film_soup.find('span',class_='sc-16ede01-0 fMPjMP').get_text()
                
                img =  'https://www.imdb.com/' + film_soup.find('a',class_='ipc-lockup-overlay ipc-focusable').get('href')
                vid = 'https://www.imdb.com/' + film_soup.find(
                        'a',class_='ipc-lockup-overlay sc-5ea2f380-2 gdvnDB hero-media__slate-overlay ipc-focusable').get('href')
                data = film_soup.find(
                        'ul',class_='ipc-metadata-list ipc-metadata-list--dividers-all ipc-metadata-list--base').find_all(
                        'div',class_='ipc-metadata-list-item__content-container')
                release_date=data[0].get_text()
                
                categories = film_soup.find(
                        'div',class_='ipc-chip-list sc-16ede01-4 bMBIRz').find_all(
                        'li',class_='ipc-inline-list__item ipc-chip__text')
                for category in categories:
                        category_list.append(category.get_text())

                cast = film_soup.find_all('a',class_='sc-18baf029-1 gJhRzH')
                for person in cast :
                        casting_list.append(person.get_text())
                
                creators = film_soup.find(
                        'ul',class_='ipc-metadata-list ipc-metadata-list--dividers-all sc-18baf029-10 jIsryf ipc-metadata-list--base').find_all(
                        'a',class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
                for creator in creators :
                        creators_list.append(creator.get_text())

                production = data[-1].find_all('a',class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
                for company in production :
                        production_comp.append(company)
                
                film_runtime = film_soup.find(
                                        'ul',class_='ipc-metadata-list ipc-metadata-list--dividers-none ipc-metadata-list--compact ipc-metadata-list--base').find_all(
                                        'div',class_='ipc-metadata-list-item__content-container')[0].get_text()

                arr = film_runtime.split(' ')
                if arr[1] == 'hours' :
                        item_type = 'Film'
                        episodes = np.nan
                        seasons = np.nan
                else :
                        item_type = 'Series'
                        episodes = film_soup.find('span',class_='ipc-title__subtext').get_text()
                        seasons = film_soup.find('select',class_='ipc-simple-select__input').get('aria-label')
                
                print('Finished')
                # print(film_url_full)
                # print(category_list)
                db = sqlite3.connect("IMDB_Scraper.db")
                cursor = db.cursor()
                cursor.execute("create table if not exists IMDB( \
                Id INTEGER PRIMARY KEY AUTOINCREMENT ,Name TEXT \
                ,Rating INTEGER ,Type TEXT ,About TEXT ,Img TEXT ,Video TEXT \
                ,Release_Date TEXT ,Categories TEXT ,Casting TEXT \
                ,Creators TEXT ,Production_Companies TEXT ,Time TEXT ,Episodes TEXT,Seasons TEXT )")

                cursor.execute(f"INSERT INTO IMDB(Name,Rating,Type,About,Img,Video,Release_Date,\
                Categories,Casting,Creators,Production_Companies,Time,Episodes,Seasons)\
                values('{name}','{rating}','{item_type}','{about}',\
                        '{img}','{vid}','{release_date}','{category_list}',\
                        '{casting_list}','{creators_list}','{production_comp}','{film_runtime}',\
                        '{episodes}','{seasons}')")
                db.commit()

                category_list.clear()
                production_comp.clear()
                creators_list.clear()
                casting_list.clear()

except sqlite3.Error as error:
        print(f'Error is {error}')



