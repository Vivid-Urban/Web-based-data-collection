# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 17:42:29 2021

@author: chenwei
"""

# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor      

def get_url_page(driver,target_url):
    driver.get(target_url)
    driver.maximize_window()
    soup = BeautifulSoup(driver.page_source, 'html.parser')   
    # scrape page
    try:
        page_list = range(int(soup.find("div", {"class": "pageNumbers"}).find_all("a")[-1].get("data-page-number")))
        results = soup.find_all('a', class_='pageNum')
        print("Total number of page: {}".format(len(page_list)))
        dataoffset=[]
        for store in results:
            unModifiedUrl = store.get("data-offset")
            dataoffset.append(int(unModifiedUrl))
        if len(dataoffset)>1:
            gap=dataoffset[1]-dataoffset[0]
        else:
            gap=30
        urls=[]
        for p in range(0,len(page_list)): 
            url_parts=target_url.split('-')
            if p==0:
                next_url=target_url
            else:
                page_number='oa'+str(p*gap)
                if it =='hotel_url' or it=='res_url':
                    url_parts.insert(2,page_number)
                if it=='shop_url':
                    url_parts.insert(4,page_number)
                next_url="-".join(url_parts)
            urls.append(next_url)          
        
    except:
        urls=[target_url]  
    return urls


def get_hotel_url(domain,soup):
    hotel_url_list=[]   
    hotel_blocks = soup.find_all('div', {"class": "prw_rup prw_meta_hsx_responsive_listing ui_section listItem"})
    for element in hotel_blocks:
        hotel_url = domain+element.find('div', {"class": "listing_title"}).find('a').get('href')
        hotel_url_list.append(hotel_url)    
    return hotel_url_list


def get_shop_url(domain,soup):
    hotel_url_list=[]   
    hotel_blocks = soup.find_all('div', {"class": "listing_info"})
    for element in hotel_blocks:
        hotel_url = domain+ element.find('a').get('href')
        hotel_url_list.append(hotel_url)  
    return hotel_url_list

def get_res_url(domain,soup):
    hotel_url_list=[]   
    hotel_blocks = soup.find_all('div', {"class": "_1llCuDZj"})
    for element in hotel_blocks:
        hotel_url = domain+element.find('div', {"class": "wQjYiB7z"}).find('a').get('href')
        hotel_url_list.append(hotel_url)
    return hotel_url_list



# get pages url
def get_urls(domain,urls,it):
    url_list=[] 
    error_url=[] 
    for url in urls:
        page = requests.get(url)
        status=page.status_code
        print (url+ "code is " + str(status))
        if status==200:  
            soup = BeautifulSoup(page.text, 'html.parser')
            if it=='hotel_url':            
                url_page=get_hotel_url(domain,soup)
                print ('get hotel url: '+url)
            if it=='res_url':
                url_page=get_res_url(domain,soup)
                print ('get restaurant url: '+url)
            if it=='shop_url':
                url_page=get_shop_url(domain,soup)   
                print ('get shop url: '+url)
                
            for u in url_page:
                url_list.append(u)            
            time.sleep(10)
        if status!=200:
            error_url.append(url)
    return url_list, error_url
    
def main(target_url,name):      
    driver = webdriver.Chrome(chrome_path, chrome_options=options)         
    domain = 'https://www.tripadvisor.com'      
    urls=get_url_page(driver,target_url)
    url_pd=pd.DataFrame()
    url_list, error_url=get_urls(domain,urls,it)    
    url_pd['URL']=url_list
    if len(error_url)>0:
        error_pd=pd.DataFrame()
        error_pd['URL']=error_url
        error_pd.to_csv(os.path.join(save_path,name+'_error.csv'))
    url_pd=url_pd.drop_duplicates(subset=['URL'])
    url_pd.to_csv(os.path.join(save_path,name+'_url.csv'))    
    driver.quit()  

    
box_path=r'E:\GISci'
# download chromedriver from https://chromedriver.chromium.org/downloads (version sensitive)
chrome_path=os.path.join(box_path,r'ex_data\chromedriver89.exe')
url_csv_path=os.path.join(box_path,r'ex_data\url_summary.csv')
url_data=pd.read_csv(url_csv_path)
url_data['Path']=url_data['Name']+"_"+url_data['State']
items=['hotel_url','res_url','shop_url']
names=url_data['Path'].to_list()
# Note: the derived class name may change, please refer to the developer mode by pressing F12
for it in items:
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    save_path=os.path.join(box_path,r'out\urls',it)
    url_pd=pd.DataFrame()
    urls_it=url_data[it].to_list()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(main,urls_it,names,timeout = 60)