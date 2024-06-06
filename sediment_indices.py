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
sf = shapefile.Reader("/Volumes/dmk/gis/limpopo/kruger/logger_sites/reference_polygons/balule/balule.shp")
shapes = sf.shapes()
points = shapes[0].points
aoi = ee.Geometry.Polygon(points)

# Define source data
image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')\
    .filterDate('2022-07-01', '2022-07-31')\
    .select('B2', 'B3', 'B4', 'B8', 'B11')

startDate = '2022-08-01'
endDate = '2024-05-12'

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

# Produce RGB image
# Expand the dimensions of the images so they can be concatenated into 3-D.
np_arr_b4 = np.expand_dims(b4, 2)
np_arr_b3 = np.expand_dims(b3, 2)
np_arr_b2 = np.expand_dims(b2, 2)
# Stack the individual bands to make a 3-D array.
rgb_img = np.concatenate((np_arr_b4, np_arr_b3, np_arr_b2), 2)
del np_arr_b2, np_arr_b3, np_arr_b4
# Scale the data to [0, 255] to show as an RGB image.
rgb_img = (255*((rgb_img)/3000)).astype('uint8')
plt.imshow(rgb_img)
plt.show()

# Normalized Difference Water Index (NDWI) 
# NDWI = ( G - NIR ) / ( G + NIR )
ndwiG = (b3-b8)/(b3+b8) # Gao
# NDWI = ( NIR - SWIR ) / ( NIR + SWIR )
ndwiM = (b8-b11)/(b8-b11) # McFeeters
# NDWI = ( G - SWIR ) / ( G + SWIR )
mndwi = (b3-b11)/(b3+b11) # Modified NDWI
water = ndwiG > -0.02


# Dekker 2002

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

#plt.imshow(wetDekker)
#plt.show()

startDate, endDate, TSS1
startDate, endDate, Secchi1
startDate, endDate, TSS2
startDate, endDate, Secchi2
startDate, endDate, TSS3
startDate, endDate, Secchi3
startDate, endDate, TSS4

