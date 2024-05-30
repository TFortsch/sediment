# Pull images and determine sediment indices for AOIs

# https://developers.google.com/earth-engine/guides/python_install
# pip install earthengine-api --upgrade
# https://developers.google.com/earth-engine/guides/auth

import ee
import numpy as np
import matplotlib.pyplot as plt

#ee.Authenticate(force=True)
# Token generated with all permissions 29 May 2024
ee.Authenticate()
ee.Initialize(project = 'ee-davidmkahler-limpopo')

# Define analysis area
balule = ee.Geometry.Polygon(
          [[31.717329298139624, -24.055719459004635],
          [31.716846500516944, -24.057384943478993],
          [31.718235884786658, -24.058736909100467],
          [31.72093418705564, -24.05800214694256],
          [31.71991494762998, -24.054984679571938]], None, False)

# Define source data
image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')\
    .filterDate('2022-07-01', '2022-07-31')\
    .select('B2', 'B3', 'B4', 'B8', 'B11')
        
# Should be built into a function from here
mosaic = image.median().clip(balule)
G = mosaic.select('B3')
R = mosaic.select('B4')
NIR = mosaic.select('B8')
SWIR = mosaic.select('B11')

# Normalized Difference Water Index (NDWI) = ( G - NIR ) / ( G + NIR )
ndwiG = (G.subtract(NIR)).divide(G.add(NIR))  # Gao
# Normalized Difference Water Index (NDWI) = ( NIR - SWIR ) / ( NIR + SWIR )
ndwiM = (NIR.subtract(SWIR)).divide(SWIR.add(NIR)) #McFeeters
# Normalized Difference Water Index (NDWI) = ( G - SWIR ) / ( G + SWIR )
mndwi = (G.subtract(SWIR)).divide(G.add(SWIR)) # Modified NDWI

# Dekker 2002
dekker = (G.add(R)).divide(2)
water = ndwiG.gte(-0.02)
wetDekker = dekker.updateMask(water)

# Find means
# https://gis.stackexchange.com/questions/350771/moving-from-earth-engine-image-to-array-for-use-in-sklearn/351177#351177
band_arrs = mosaic.sampleRectangle(region=balule)

# Get individual band arrays.
band_arr_b4 = band_arrs.get('B4')
band_arr_b5 = band_arrs.get('B5')
band_arr_b6 = band_arrs.get('B6')

# Transfer the arrays from server to client and cast as np array.
np_arr_b4 = np.array(band_arr_b4.getInfo())
np_arr_b5 = np.array(band_arr_b5.getInfo())
np_arr_b6 = np.array(band_arr_b6.getInfo())
print(np_arr_b4.shape)
print(np_arr_b5.shape)
print(np_arr_b6.shape)

# Expand the dimensions of the images so they can be concatenated into 3-D.
np_arr_b4 = np.expand_dims(np_arr_b4, 2)
np_arr_b5 = np.expand_dims(np_arr_b5, 2)
np_arr_b6 = np.expand_dims(np_arr_b6, 2)
print(np_arr_b4.shape)
print(np_arr_b5.shape)
print(np_arr_b6.shape)

# Stack the individual bands to make a 3-D array.
rgb_img = np.concatenate((np_arr_b6, np_arr_b5, np_arr_b4), 2)
print(rgb_img.shape)

# Scale the data to [0, 255] to show as an RGB image.
rgb_img_test = (255*((rgb_img - 100)/3500)).astype('uint8')
plt.imshow(rgb_img_test)
plt.show()