# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 21:37:05 2021

@author: chenwei
"""


import arcpy
import pandas as pd
from osgeo import ogr
import os

# input: city boundary with projection of WGS 1984 World Mercator
# output: a csv with center point location for Google Map picture retrival and a tif file for picture conversion


def read_shp_astable(filename):
    ds = ogr.Open(filename, False)  
    layer = ds.GetLayer(0)  
    lydefn = layer.GetLayerDefn() 
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
    reclist_csv=pd.DataFrame(reclist)
    return reclist_csv

def generate_grids(input_boundary,zoomlevel,output_grids):

    # get grid extent
    desc = arcpy.Describe(input_boundary)
    
    xmin = desc.extent.XMin
    xmax = desc.extent.XMax
    ymin = desc.extent.YMin
    ymax = desc.extent.YMax

    if zoomlevel==18:
        metersPerPx=0.5967
    if zoomlevel==15:
        metersPerPx=4.756 
    
    # picture size =600*600
    width=metersPerPx*600
    
    fishnet_shp =output_grids+"\\"+'grid.shp'
    label_shp = output_grids+"\\"+'grid_label.shp'
    proj_shp_label=output_grids+"\\"+'grid_label_proj.shp'
    proj_shp_poly=output_grids+"\\"+'grid_proj.shp'
    fishnet_tif=output_grids+"\\"+'grid_geo.tif'
    
    # parameter preparation		
    ori_cord=str(xmin)+" "+str(ymin)
    y_cord=str(xmin)+" "+str(ymin+10)
    corner_cord=str(xmax)+" "+str(ymax)
    template_ext=str(xmin)+" "+str(ymin)+" "+str(xmax)+" "+str(ymax)
    
    # Process: Create grid
    arcpy.CreateFishnet_management(out_feature_class=fishnet_shp, origin_coord=ori_cord, y_axis_coord=y_cord, cell_width=width, cell_height=width, number_rows="", number_columns="", corner_coord=corner_cord, labels="LABELS", template=template_ext, geometry_type="POLYGON")
    
    arcpy.Project_management(in_dataset=fishnet_shp, out_dataset=proj_shp_poly, out_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", transform_method="", in_coor_system="PROJCS['WGS_1984_World_Mercator',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],UNIT['Meter',1.0]]", preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")
    arcpy.Project_management(in_dataset=label_shp, out_dataset=proj_shp_label, out_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", transform_method="", in_coor_system="PROJCS['WGS_1984_World_Mercator',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],UNIT['Meter',1.0]]", preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")
    
    arcpy.AddXY_management(proj_shp_label)
    
    arcpy.conversion.PointToRaster(in_features=label_shp, value_field="FID", out_rasterdataset=fishnet_tif, cell_assignment="MOST_FREQUENT", priority_field="NONE", cellsize=width)
    
    # get intersected grids with city boundary
    sp_out=output_grids+"\\"+'grid_sp.shp'  
    arcpy.SpatialJoin_analysis(target_features=fishnet_shp, join_features=input_boundary, out_feature_class=sp_out, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", match_option="INTERSECT")

    # get center lat and lon for static map we need to obtain
    sp_grids=read_shp_astable(sp_out)[['Join_Count','TARGET_FID']]
    cpoints=read_shp_astable(proj_shp_label)[['POINT_X','POINT_Y']]
    cpoints['FID']=range(0,len(cpoints))
    
    cpoint_sp = pd.merge(cpoints, sp_grids,how='left', left_on='FID', right_on='TARGET_FID')
    out_csv_path=output_grids+'\\'+'center_latlon.csv'
    cpoint_sp.to_csv(output_grids+'\\'+'center_latlon.csv')
    print ('Finish generating grid')
    return out_csv_path
    

dir_ori=r'E:\GISci'
input_boundary=dir_ori+"\\"+'ex_data\MI_Rochester.shp'
output_grids=r'E:\GISci\out\grid'
if os.path.exists(output_grids) ==False:
    os.mkdir(output_grids)

zoomlevel=18    
out_csv_path=generate_grids(input_boundary,zoomlevel,output_grids)



    