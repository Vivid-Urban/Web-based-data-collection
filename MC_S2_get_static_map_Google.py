# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 22:53:49 2021

@author: chenwei
"""

import os
import pandas as pd
from io import BytesIO
from urllib import request
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

def merge_torow_nocrop(rows,cols,city_shp_name): 
    
    new_im = Image.new('RGB', (600*cols,600))
    st_order=list(range(0,600*cols,600))
    
    for j in range(0,rows):       
        for i in range(0,cols):  
            png_name=i+j*cols
            png_path=png_folder+"\\"+str(png_name)+'crop.png'  
            #I change brightness of the images, just to emphasise they are unique copies.
            im=Image.open(png_path)  
            new_im.paste(im, (st_order[i],0))
        #new_im.show()    
        new_im.save(png_folder+'\\'+"Row"+str(j+1)+".png",optimize=True, quality=500)
        print('finish '+str(j+1))               
    
def merge_tocol_nocrop(rows,cols,city_shp_name): 
    
    new_im = Image.new('RGB', (600*cols,600*rows))
    st_order=list(range(0,600*rows,600))
      
    for i in range(rows,0,-1):  
        png_path=png_folder+"\\"+"Row"+str(i)+'.png'  
        #I change brightness of the images, just to emphasise they are unique copies.
        im=Image.open(png_path)  
        left=0
        top=0
        right=600*cols
        bottom=600
        im_crop = im.crop((left, top, right, bottom)) 
        new_im.paste(im_crop, (0,st_order[rows-i]))
    new_im.show()    
    new_im.save(png_folder+'\\'+city_shp_name+".png",optimize=True, quality=500)
    
dir_ori=r'E:\GISci'
city_shp_name='MI_Rochester'
output_grids=r'E:\GISci\out\grid'
out_csv_path=output_grids+'\\'+'center_latlon.csv'
png_folder=dir_ori+"\\"+"out\Google_Png"

if os.path.exists(png_folder) ==False:
    os.mkdir(png_folder)
    
grid_csv=pd.read_csv(out_csv_path)    
   
zoomlevel=19
# map style can be set in map styles tab of google maps plarform
mapid='yourmapid'
yourkey='yourkey'
 
cols=len(set(grid_csv["POINT_X"].to_list()))
rows=len(set(grid_csv["POINT_Y"].to_list()))

# get google static map picture gird by grid
# the grid located outside of city will be retrived as the pre-prepared white picture (same size, to save the cost)

for i in range(0,len(grid_csv)):
    if grid_csv.iloc[i]['Join_Count']!=0:     
        
        lat=grid_csv.iloc[i]['POINT_Y']
        lon=grid_csv.iloc[i]['POINT_X']
            
        url1 = 'https://maps.googleapis.com/maps/api/staticmap?'
        url2 = 'center='+str(round(lat,6))+','+str(round(lon,6))
                
        url3 = url1+'size=640x640&zoom='+str(zoomlevel)+'&'+url2+'&map_id='+mapid+'&key='+yourkey
    
        buffer = BytesIO(request.urlopen(url3).read())
        image = Image.open(buffer)
        png_path=png_folder+"\\"+str(i)+'.png'
        image.save(png_path)    
    
        im=Image.open(png_path)  
        left=20
        top=20
        right=640-left
        bottom=640-top
        im_crop = im.crop((left, top, right, bottom))  
        # to remove credits of google map
        im_crop.save(png_folder+"\\"+str(i)+'crop.png',optimize=True, quality=500)   
        print (i)
                
    if grid_csv.iloc[i]['Join_Count']==0:     
        source=dir_ori+"\\"+'ex_data\white.png'
        im=Image.open(source)  
        left=20
        top=20
        right=640-left
        bottom=640-top
        im_crop = im.crop((left, top, right, bottom))  
        im_crop.save(png_folder+"\\"+str(i)+'crop.png',optimize=True, quality=500)        

merge_torow_nocrop(rows,cols,city_shp_name)
merge_tocol_nocrop(rows,cols,city_shp_name)
print ('finish '+city_shp_name)

    
        
    