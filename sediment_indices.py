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

balule = ee.Geometry.Polygon(
          [[31.717329298139624, -24.055719459004635],
          [31.716846500516944, -24.057384943478993],
          [31.718235884786658, -24.058736909100467],
          [31.72093418705564, -24.05800214694256],
          [31.71991494762998, -24.054984679571938]])

# balule =  # Shapefile import

image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')\
    .filterBounds(balule)\
    .filterDate('2022-07-01', '2022-07-31')\
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))\
    .select('B2', 'B3', 'B4', 'B8', 'B11')
        

mosaic = image.median().clip(balule)
image_rgb = image.visualize(bands=['B5', 'B4', 'B3'], max=0.5)

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

avg = wetDekker.reduceRegion(**{
    'geometry': balule.getInfo(),
    'reducer': ee.Reducer.mean(),
  })

# https://gis.stackexchange.com/questions/350771/moving-from-earth-engine-image-to-array-for-use-in-sklearn/351177#351177

