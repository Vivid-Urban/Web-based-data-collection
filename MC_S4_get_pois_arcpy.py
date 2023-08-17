# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 15:43:09 2023

@author: chenwei
"""

import arcpy
from osgeo import ogr
import os
import pandas as pd
import numpy as np

def read_shp(filename):
    ds = ogr.Open(filename, False)  
    layer = ds.GetLayer(0)  
    spatialref = layer.GetSpatialRef() 
    lydefn = layer.GetLayerDefn() 
    geomtype = lydefn.GetGeomType() 
    fieldlist = [] 
    for i in range(lydefn.GetFieldCount()):
        fddefn = lydefn.GetFieldDefn(i)
        fddict = {'name':fddefn.GetName(),'type':fddefn.GetType(),
                  'width':fddefn.GetWidth(),'decimal':fddefn.GetPrecision()}
        fieldlist += [fddict]
    geomlist, reclist = [], [] 
    feature = layer.GetNextFeature() 
    while feature is not None:
        geom = feature.GetGeometryRef()
        geomlist += [geom.ExportToWkt()]
        rec = {}
        for fd in fieldlist:
            rec[fd['name']] = feature.GetField(fd['name'])
        reclist += [rec]
        feature = layer.GetNextFeature()
    ds.Destroy() 
    return spatialref,geomtype,geomlist,fieldlist,reclist

def write_shp(filename,spatialref,geomtype,geomlist,fieldlist,reclist):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if os.access(filename, os.F_OK ): 
        driver.DeleteDataSource(filename)
    ds = driver.CreateDataSource(filename) 
    layer = ds.CreateLayer(filename [:-4], srs=spatialref, geom_type=geomtype) 

    for fd in fieldlist:
        field = ogr.FieldDefn(fd['name'],fd['type'])
        fd_keys=fd.keys()
        if 'width' in fd_keys:
            field.SetWidth(fd['width'])
        if 'decimal'in fd_keys:
            field.SetPrecision(fd['decimal'])
        layer.CreateField(field)
    for i in range(len(reclist)):  
        geom = ogr.CreateGeometryFromWkt(geomlist[i])
        feat = ogr.Feature(layer.GetLayerDefn())  
        feat.SetGeometry(geom)
        for fd in fieldlist:
            feat.SetField(fd['name'], reclist[i][fd['name']])
        layer.CreateFeature(feat) 
    ds.Destroy()


def gene_POI(city_shp_name):
    out_tif=output_grids+"\\"+city_shp_name+'.tif'
    poi_shp=output_grids+"\\"+city_shp_name+'.shp'
    poi_shp_poly=output_grids+"\\"+city_shp_name+'no0.shp'
    poi_result=output_grids+"\\"+city_shp_name+'_POI_poly.shp'
    poi_out=output_grids+"\\"+city_shp_name+'_POIs.shp'
    # convert geotif file to polygon shapefile
    arcpy.conversion.RasterToPolygon(in_raster=out_tif, out_polygon_features=poi_shp, simplify="NO_SIMPLIFY", raster_field="Value", create_multipart_features="SINGLE_OUTER_PART")
    spatialref,geomtype,geomlist,fieldlist,reclist=read_shp(poi_shp)    
    shp_df=pd.DataFrame(reclist)
    shp_df['FID']=range(0,len(reclist))
    grid0=shp_df[shp_df['gridcode']==0]['FID'].to_list()
    # only keep POI polygons
    geomlist_new=[]
    reclist_new=[]
    for d in range(0,len(reclist)):
        if d not in grid0:
            geomlist_new.append(geomlist[d])
            reclist_new.append(reclist[d])   
    write_shp(poi_shp_poly,spatialref,geomtype,geomlist_new,fieldlist,reclist_new)
    print (city_shp_name)
    
    # remove duplicated part of POI polygon   
    arcpy.Near_analysis(in_features=poi_shp_poly, near_features=poi_shp_poly, search_radius="", location="NO_LOCATION", angle="NO_ANGLE", method="PLANAR")           
    arcpy.management.CalculateGeometryAttributes(in_features=poi_shp_poly, geometry_property=[["Areas", "AREA"]], area_unit="SQUARE_METERS", coordinate_format="SAME_AS_INPUT")[0]
    spatialref,geomtype,geomlist,fieldlist,reclist=read_shp(poi_shp_poly)
    shp_df_dist=pd.DataFrame(reclist)
    shp_df_dist['FID']=range(0,len(reclist))
    dup_poi=shp_df_dist[(shp_df_dist['NEAR_DIST']==0)&(shp_df_dist['Areas']<20)]['FID'].to_list()
    small_patch=shp_df_dist[shp_df_dist['Areas']<=15]['FID'].to_list()    
    geomlist_new=[]
    reclist_new=[]    
    for d in range(0,len(reclist)):
        if d not in dup_poi and d not in small_patch:
            geomlist_new.append(geomlist[d])
            reclist_new.append(reclist[d])     

    write_shp(poi_result,spatialref,geomtype,geomlist_new,fieldlist,reclist_new)
    
    # convert polygon to point
    spatialref,geomtype,geomlist,fieldlist,reclist=read_shp(poi_result)
    geomtype_new=1
    geomlist_new=[]
    for g in geomlist:
        points=g[9:-1]
        remove=points.replace('(', '').replace(')', '')
        pnt_x=[]
        pnt_y=[]        
        pnts=remove.split(',')
        for r in pnts:
            xy=r.split(' ')
            pnt_x.append(float(xy[0]))
            pnt_y.append(float(xy[1]))
        min_y=np.min(pnt_y)
        min_loc=pnt_y.index(min_y)
        min_pont='POINT ('+str(pnt_x[min_loc])+' '+str(pnt_y[min_loc])+')'
        geomlist_new.append(min_pont)
    
    write_shp(poi_out,spatialref,geomtype_new,geomlist_new,fieldlist,reclist)
    print ('finish generate POI in '+city_shp_name)
    

city_shp_name='MI_Rochester'
output_grids=r'E:\GISci\out\grid'
gene_POI(city_shp_name)
