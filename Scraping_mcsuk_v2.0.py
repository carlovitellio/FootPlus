# -*- coding: utf-8 -*-
"""
Created on Fri May  7 23:57:20 2021

@author: Carlo
"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time 
import pandas as pd

def download_image(url_img, pathname, name):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    
    options = Options()
    options.headless = True
    options.add_argument("--window-size=300,300")
    driver_img = webdriver.Chrome(options=options, executable_path=r'C:/Program Files/chromedriver.exe')
    driver_img.get(url_img)
    driver_img.save_screenshot(pathname + name + '.png')
    driver_img.close()
    

# Salvo le immagini prendendole dalle pagine iniziali
# Non necessario ripetere questa procedura più di una volta 
img_path = 'C:/Users/Carlo/Documents/GitHub/FootPlus/images/New_images/'

for i in range(9):
    url = f"https://www.mcsuk.org/goodfishguide/?page={i+1}"
    driver = webdriver.Chrome(executable_path=r'C:/Program Files/chromedriver.exe')
    driver.implicitly_wait(10)
    driver.get(url)
    for elem in driver.find_elements_by_xpath('//img[@class="css-1lx0098"]'):
        img_name = elem.get_attribute('alt')
        img_url = elem.get_attribute('src')
        download_image(img_url, img_path, img_name)
    driver.close()
    

# Creo una lista che contenga tutti gli indirizzi delle pagine dei singoli pesci
all_fish_urls =  []
for i in range(9):
    url = f"https://www.mcsuk.org/goodfishguide/?page={i+1}"
    driver = webdriver.Chrome(executable_path=r'C:/Program Files/chromedriver.exe')
    driver.get(url)
    time.sleep(1)
    fish_urls = driver.find_elements_by_xpath('//a[@class="css-vurnku"]')
    fish_urls.pop(0)
    for elem in fish_urls:
        all_fish_urls.append(elem.get_attribute('href'))
    driver.close()

fish_names = [a.split('/')[-2] for a in all_fish_urls]

df = pd.DataFrame()

for fish_url in all_fish_urls:
    try:
        driver = webdriver.Chrome(executable_path=r'C:/Program Files/chromedriver.exe')
        driver.get(fish_url)
        time.sleep(1.2)
        fish_name = driver.find_elements_by_xpath('//h1[@class="css-16d65tb"]')[0].text
        
        for elem in driver.find_elements_by_xpath('//div[@class="css-7ogzof"]'):
            df_loc = pd.DataFrame(elem.text.split('\n')).T
            df_loc = pd.concat([df_loc, pd.DataFrame.from_dict({'fish_name': fish_name}, orient='index').T], ignore_index=False, axis=1)
            df = df.append(df_loc)
        driver.close()
    except:
        driver = webdriver.Chrome(executable_path=r'C:/Program Files/chromedriver.exe')
        driver.get(fish_url)
        time.sleep(1.2)
        
        for elem in driver.find_elements_by_xpath('//div[@class="css-7ogzof"]'):
            df_loc = pd.DataFrame(elem.text.split('\n')).T
            df_loc = pd.concat([df_loc, pd.DataFrame.from_dict(
                {'fish_name': fish_name}, orient='index').T], ignore_index=False, axis=1)
            df = df.append(df_loc)
        driver.close()


        
print(len(df.fish_name.unique()))
df.sort_values(by='fish_name', inplace=True)
df.rename(columns={0: 'Rating', 1: 'Where', 2: 'Location', 3: 'Method', 4:'Certification'}, inplace=True)
df.Location = df.Location.apply(str.replace, args = ('Location:',''))
df.Method = df.Method.apply(str.replace, args = ('Method:',''))
df.Certification = df.Certification.apply(str.replace, args = ('Certification:',''))
df.Certification = df.Certification.apply(str.replace, args = ('More info',''))
df.drop(columns=5, inplace=True)
df.to_csv('metodi_pesca.csv', index=False)



df_scoring = pd.DataFrame()

for fish_url in all_fish_urls:
    driver = webdriver.Chrome(executable_path=r'C:/Program Files/chromedriver.exe')
    driver.get(fish_url)
    time.sleep(1.5)
    fish_name = driver.find_elements_by_xpath('//h1[@class="css-16d65tb"]')[0].text
    for elem in driver.find_elements_by_xpath('//a[@class="css-1b0zgfz"]'):
        try:
            details_url = elem.get_attribute('href')
            driver_detail = webdriver.Chrome(executable_path=r'C:/Program Files/chromedriver.exe')
            driver_detail.get(details_url)
            time.sleep(1.2)
            scores = []
            criteria = []
            for score in driver_detail.find_elements_by_xpath('//div[@class="css-zkfaav"]'):
                text = score.text.split('\n')
                if len(text) == 2:
                    score, criterium = text
                    scores.append(score)
                    criteria.append(criterium)

            df_loc = pd.DataFrame.from_dict(dict(zip(criteria, scores)), orient='index').T            
            df_loc = pd.concat([df_loc, pd.DataFrame.from_dict(
                {'fish_name': fish_name}, orient='index').T], ignore_index=False, axis=1)
            df_scoring = df_scoring.append(df_loc)
            driver_detail.close()
        except:
            print('Bestemmia')
            print(elem)
    driver.close()
                    
print(len(df_scoring.fish_name.unique()))
df_scoring.sort_values(by='fish_name', inplace=True)
df_tot = pd.concat([df, df_scoring.drop(columns='fish_name')], axis=1)

df_tot.to_csv('FishingScores.csv', index=False)