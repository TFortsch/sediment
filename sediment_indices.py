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

#ee.Authenticate(force=True)
# Token generated with all permissions 29 May 2024, DMK
ee.Authenticate()
ee.Initialize(project = 'ee-fortschthomas52')

# Define analysis area
balule = ee.Geometry.Polygon(
          [[31.717329298139624, -24.055719459004635],
          [31.716846500516944, -24.057384943478993],
          [31.718235884786658, -24.058736909100467],
          [31.72093418705564, -24.05800214694256],
          [31.71991494762998, -24.054984679571938]], None, False)
# the analysis area is transformed into a rectangle in the .sampleRectangle/.getInfo phases

# Define source data
image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')\
    .filterDate('2022-07-01', '2022-07-31')\
    .select('B2', 'B3', 'B4', 'B8', 'B11')

# CRS is not the same.
# proj = image.first().select('B2').projection() # EPSG:32656, UTM zone 56N (Siberia?)
# proj = balule.projection() # EPSG:4326

# Export arrays
# https://gist.github.com/jdbcode/f4d56d72f7fc5beeaa3859999b1f5c3d
# https://gist.github.com/jdbcode/f4d56d72f7fc5beeaa3859999b1f5c3d?permalink_comment_id=3355627#gistcomment-3355627
mosaic = image.median().reproject(crs='EPSG:32736', scale=1) # This allows us to set the resolution.
band_arrs = mosaic.sampleRectangle(region=balule)

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

# Dekker 2002
dekker = (b3+b4)/2
water = ndwiG > -0.02
wetDekker = dekker * water
plt.imshow(wetDekker)
plt.show()

meanDekker = np.mean(wetDekker) * np.product(wetDekker.shape) / np.sum(wetDekker>0)
