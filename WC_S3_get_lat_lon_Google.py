# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 14:27:07 2021

@author: chenwei
"""

import glob
import pandas as pd
import requests
import os


def extract_lat_long_via_address(address_or_zipcode):
    lat, lng = 0, 0
    api_key = GOOGLE_API_KEY
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={address_or_zipcode}&key={api_key}"
    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        return 0, 0
    try:
        results = r.json()['results'][0]
        lat = results['geometry']['location']['lat']
        lng = results['geometry']['location']['lng']
    except:
        pass
    return lat, lng

def main(csv):
    url_dt=pd.read_csv(csv)
    url_dt['lat']=[0]*len(url_dt)
    url_dt['lng']=[0]*len(url_dt)    

    for u in range(0,len(url_dt)):
        ser=url_dt.iloc[u]
        if ser['signal']=='finish':
            add=ser['address']
            lat,lng=extract_lat_long_via_address(add)
            if lat==0 or lng==0:
                city=add.split(',')[-2]
                state=add.split(',')[-1]
                ele_list=add.split(',')[0].split('#')
                if len(ele_list)>1:
                    add_new=ele_list[0]+','+city+','+state
                    lat,lng=extract_lat_long_via_address(add_new)                
            url_dt.loc[u,'lat']=lat
            url_dt.loc[u,'lng']=lng            
            name_h=csv.split('\\')[-1]
            content_path=os.path.join(box_path,r'out\pnt',it,name_h)
            url_dt.to_csv(content_path)


        
box_path=r'E:\GISci'
items=['hotel_url','res_url','shop_url']
for it in items:
    add_path=os.path.join(box_path,r'out\address',it)+"\*.csv"
    filelist = glob.glob(add_path)  
    GOOGLE_API_KEY = 'yourkey' 
    
    for i in range(0,len(filelist)):
        main(filelist[i])
        print (i) 