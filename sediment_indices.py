# Pull images and determine sediment indices for AOIs
# Remember to update ee.Initialize() with authenticated project - LINE 18

# Initial attempt in GEE:
# https://code.earthengine.google.com/77a2e41436a615fe1c04c21fec61e9d0

# https://developers.google.com/earth-engine/guides/python_install
# pip install earthengine-api --upgrade
# https://developers.google.com/earth-engine/guides/auth

import ee
import numpy as np
import matplotlib.pyplot as plt
import shapefile

#ee.Authenticate(force=True)
ee.Authenticate()
ee.Initialize(project = 'ee-fortschthomas52')
#ee.Initialize(project = 'ee-davidmkahler-limpopo')

# Define analysis area
# the analysis area is transformed into a rectangle in the .sampleRectangle/.getInfo phases
# enter shapefiles here:
#sf = shapefile.Reader("/Volumes/dmk/gis/limpopo/kruger/logger_sites/reference_polygons/balule/balule.shp")
sf = shapefile.Reader("/Users/hydro3/Documents/KrugerSensors/reference_polygons/balule/balule.shp")
shapes = sf.shapes()
points = shapes[0].points
aoi = ee.Geometry.Polygon(points)

start = '2022-08-01'
end = '2022-08-10'

def pulldata(startDate, endDate):
    # Define source data
    image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')\
        .filterDate(startDate, endDate)\
        .select('B2', 'B3', 'B4', 'B8', 'B11')

# CRS is not the same.
# proj = image.first().select('B2').projection() # EPSG:32656, UTM zone 56N (Siberia?)
# proj = balule.projection() # EPSG:4326

# Export arrays
# https://gist.github.com/jdbcode/f4d56d72f7fc5beeaa3859999b1f5c3d
# https://gist.github.com/jdbcode/f4d56d72f7fc5beeaa3859999b1f5c3d?permalink_comment_id=3355627#gistcomment-3355627
    mosaic = image.median().reproject(crs='EPSG:32736', scale=1) # This allows us to set the resolution.
    band_arrs = mosaic.sampleRectangle(region=aoi)

# Get individual band arrays.
    band_arr_b2 = band_arrs.get('B2')   # Blue
    band_arr_b3 = band_arrs.get('B3')   # Green
    band_arr_b4 = band_arrs.get('B4')   # Red
    band_arr_b8 = band_arrs.get('B8')   # NIR
    band_arr_b11 = band_arrs.get('B11') # SWIR

# Transfer the arrays from server to client and cast as np array.
    b2 = np.array(band_arr_b2.getInfo())   # b2  Blue
    b3 = np.array(band_arr_b3.getInfo())   # b3  Green
    b4 = np.array(band_arr_b4.getInfo())   # b4  Red
    b8 = np.array(band_arr_b8.getInfo())   # b8  NIR
    b11 = np.array(band_arr_b11.getInfo()) # b11 SWIR

# Normalized Difference Water Index (NDWI) 
# NDWI = ( G - NIR ) / ( G + NIR )
    ndwiG = (b3-b8)/(b3+b8) # Gao
# NDWI = ( NIR - SWIR ) / ( NIR + SWIR )
    ndwiM = (b8-b11)/(b8-b11) # McFeeters
# NDWI = ( G - SWIR ) / ( G + SWIR )
    mndwi = (b3-b11)/(b3+b11) # Modified NDWI
    water = ndwiG > -0.02

    TSS1 = (b3+b4)/2
    TSS1 = TSS1 * water
    TSS1 = np.sum(TSS1) / np.sum(TSS1>0)

    Secchi1 = (b2/b4)
    Secchi1 = Secchi1 * water
    Secchi1 = np.sum(Secchi1)/ np.sum(Secchi1>0)

    TSS2 = (b3/b4)
    TSS2 = TSS2 * water
    TSS2 = np.sum(TSS2) / np.sum(TSS2>0)

    Secchi2 = (b4/b3)
    Secchi2 = Secchi2 * water
    Secchi2 = np.sum(Secchi2)/ np.sum(Secchi2>0)

    TSS3 = (b8/b3 , b8/b4)
    TSS3 = TSS3 * water
    TSS3 = np.sum(TSS3) / np.sum(TSS3>0)

    Secchi3 = (b4/b2)+b2
    Secchi3 = Secchi3 * water
    Secchi3 = np.sum(Secchi3)/ np.sum(Secchi3>0)

    TSS4 = (b4/b3)+b8
    TSS4 = TSS4 * water
    TSS4 = np.sum(TSS4) / np.sum(TSS4>0)

    f = open("Sediment_Indices.txt", "a")
    f.write(str(startDate) + ", " + str(endDate) + ", " + str(TSS1) + ", " + 
            str(Secchi1) + ", " + 
            str(TSS2) + ", " + str(Secchi2) + ", " + 
            str(TSS3) + ", " + str(Secchi3) + ", " + str(TSS4) + '\n') 
    f.close()

