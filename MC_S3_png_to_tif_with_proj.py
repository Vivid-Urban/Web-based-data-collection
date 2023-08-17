# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 14:47:43 2023

@author: chenwei
"""

from osgeo import gdal
import numpy as np
from PIL import Image
import pandas as pd
import math
import numpy.ma as ma
from skimage.morphology import skeletonize
import numpy as np
from skimage import morphology
import scipy
Image.MAX_IMAGE_PIXELS = None

def read_img(filename):
    dataset=gdal.Open(filename) 
    im_width = dataset.RasterXSize  
    im_height = dataset.RasterYSize 
    im_bands = dataset.RasterCount  
    im_geotrans = dataset.GetGeoTransform()  
    im_proj = dataset.GetProjection() 
    im_data = dataset.ReadAsArray(0,0,im_width,im_height)
    del dataset 
    return im_proj,im_geotrans,im_data

def write_img(filename,im_proj,im_geotrans,im_data):
    datatype=gdal.GDT_Byte
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1,im_data.shape 
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)
    dataset.SetGeoTransform(im_geotrans) #写入仿射变换参数
    dataset.SetProjection(im_proj) #写入投影
    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)  #写入数组数据
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i+1).WriteArray(im_data[i])
    del dataset

# recognize RGB according to your cutomized map style
def label_color(png_path):     
    pic = Image.open(png_path).convert('RGB')
    pix_array = np.array(pic)  
    row,col,band=pix_array.shape
    pix_other_mask=np.logical_and(pix_array[:,:,1]!=0,pix_array[:,:,2]!=0,pix_array[:,:,0]!=0)
    # background is white
    pix_back_mask=np.logical_and(pix_array[:,:,0] ==254,pix_array[:,:,1]==254,pix_array[:,:,2]==254)
    # office is 0 0 0 (black)
    pix_office_mask=np.logical_and(pix_array[:,:,0] == 0,pix_array[:,:,1] == 0,pix_array[:,:,2]== 0)
    # shop is 0 255 0 (green)
    pix_shop_mask=np.logical_and(pix_array[:,:,1]>0,pix_array[:,:,2]== 0,pix_array[:,:,0] == 0)
    # restaurant is 0 0 255 (blue)
    pix_restaurant_mask=np.logical_and(pix_array[:,:,2]>0,pix_array[:,:,0] == 0,pix_array[:,:,1] == 0)
    # hotel is 255 255 0 (yellow)
    pix_hotel_mask=np.logical_and(pix_array[:,:,2]== 0,pix_array[:,:,0]>0,pix_array[:,:,1]>0)
    # medical is 255 0 0 (red)
    pix_medical_mask=np.logical_and(pix_array[:,:,0]>0,pix_array[:,:,1] == 0,pix_array[:,:,2]== 0)
    # school is 255 0 255 (pink)
    pix_school_mask=np.logical_and(pix_array[:,:,0]>0,pix_array[:,:,2]>0,pix_array[:,:,1] == 0)
    pix_new=np.zeros((row,col),dtype=int)
    pix_new[pix_office_mask]=1    
    pix_new[pix_shop_mask]=2
    pix_new[pix_restaurant_mask]=3    
    pix_new[pix_hotel_mask]=4
    pix_new[pix_medical_mask]=5    
    pix_new[pix_school_mask]=6    
    pix_new[pix_other_mask]=7    
    pix_new[pix_back_mask]=99    
    selem = morphology.disk(2)
    pixnew = morphology.erosion(pix_new, selem)    
    pixnew[pix_back_mask]=0    
    return pixnew

dir_ori=r'E:\GISci'
city_shp_name='MI_Rochester'
png_folder=dir_ori+"\\"+"out\Google_Png"
png_path=png_folder+"\\"+city_shp_name+'.png'
output_grids=r'E:\GISci\out\grid'
pixnew=label_color(png_path)
fishnet_tif=output_grids+"\\"+'grid_geo.tif'
im_proj,im_geotrans,im_data=read_img(fishnet_tif)
zoomlevel=18


if zoomlevel==18:
    metersPerPx=0.5967
if zoomlevel==15:
    metersPerPx=4.756 

im_geotrans_new=(im_geotrans[0],metersPerPx,0.0,im_geotrans[3],0.0,metersPerPx*(-1))
out_tif=output_grids+"\\"+city_shp_name+'4.tif'
write_img(out_tif,im_proj,im_geotrans_new,pixnew)
    
