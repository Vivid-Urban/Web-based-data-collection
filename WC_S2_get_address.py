# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 14:47:58 2021

@author: chenwei
"""
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import time
import glob
import os
from concurrent.futures import ThreadPoolExecutor      

# Note: the derived class name may change, please refer to the developer mode by pressing F12
def get_content(soup,it):
    if it=='hotel_url':            
        info_block = soup.find_all('span', {"class": "_3ErVArsu jke2_wbp"})[1]
        address =info_block.text   
        print ('get address: '+address)
    if it=='res_url':
        info_block = soup.find_all('a', {"class": "_15QfMZ2L"})[1]
        address =info_block.text   
        print ('get address: '+address)
    if it=='shop_url':
        info_block = soup.find_all('div', {"class": "LjCWTZdN"})[0] 
        address =info_block.text   
        print ('get address: '+address)     
    return address

def parse_hotel(url):
    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}
    
    try:
        r = requests.get(url, headers=header)
        status=r.status_code
        if status==200:
            soup = BeautifulSoup(r.text, 'html.parser')
            try:
                address =get_content(soup,it)
                signal='finish'   
            except:
                address='None'
                signal='again'    
        if status!=200:  
            signal='again'  
            address='None'                
    except:
        address='None'  
        signal='again'
    time.sleep(10)
    return address, signal
   
def main(csv):
    url_dt=pd.read_csv(csv)
    againlg=len(url_dt[url_dt['signal']=='again'])
    if againlg>0:
        for u in range(0,len(url_dt)):
            ser=url_dt.iloc[u]
            if ser['signal']=='again':
                url=ser['URL']
                address, signal=parse_hotel(url)
                url_dt.loc[u,'address']=address
                url_dt.loc[u,'signal']=signal            
                name_h=csv.split('\\')[-1]
                content_path=os.path.join(box_path,r'out\address',it,name_h)
                url_dt.to_csv(content_path)
    if againlg==0:
        name_h=csv.split('\\')[-1]
        content_path=os.path.join(box_path,r'out\address',it,name_h)
        url_dt.to_csv(content_path)
   
box_path=r'E:\GISci'
items=['hotel_url','res_url','shop_url']
for it in items:
    save_path=os.path.join(box_path,r'out\urls',it)
    csvs=glob.glob(save_path+"\\"+"*.csv")
             
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(main,csvs,timeout = 60)        
    
    
    




