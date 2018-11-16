import ee
import numpy as np
from PIL import Image
import os
import requests
import zipfile
import datetime


if __name__ == '__main__':
    # Initialize earth engine
    ee.Initialize()

    # Define your desired area of landsat data here
    polygon = ee.Geometry.Polygon(
	        [[[-79.75, 42.25],
	          [-79.75, 42],
	          [-75.35, 42],
	          [-74.7, 41.35],
	          [-75.15, 40.7],
	          [-74.75, 40.15],
	          [-75.47, 39.75],
	          [-75.8, 39.7],
	          [-80.5, 39.7],
	          [-80.5, 42.25]]])
    lat_bound1 = -80.5
    lat_bound2 = -74.7
    lon_bound1 = 39.7
    lon_bound2 = 42.3
    step_len = 0.05

    # This is a sample for NAIP/DOQQ data, feel free to modify to accomodate your own need
    collection_name = "USDA/NAIP/DOQQ"
    date_filter = ee.Filter.date('2017-01-01', '2018-12-31') # Note that not all Javascript API works for Python so be careful with ee.Filter , ImageCollection's filter methods may be good alternatives

    # Take data
    collection = ee.ImageCollection(collection_name).filter(date_filter)
    collection = collection.filterBounds(polygon)
    # Select specific channel and mosaic to large images
    trueColor = collection.select(['R', 'G', 'B'])
    NIR = collection.select(['N'])
    trueColor = trueColor.mosaic()
    NIR = NIR.mosaic()

    # State / City size images are usually too large for exporting, so the images are cropped into tiles and downloaded. Usually 3000x3000 is a good size.
    for lat in np.arange(lat_bound1, lat_bound2, step_len):
      for lon in np.arange(lon_bound1, lon_bound2, step_len):

        # Crop image and get download url
        rect = ee.Geometry.Polygon([[[lat, lon], [lat, lon+step_len], [lat-step_len, lon+step_len], [lat-step_len, lon]]])
        path = trueColor.getDownloadUrl({'scale':1, 'region':rect.getInfo()['coordinates']})
        path2 = NIR.getDownloadUrl({'scale': 1, 'region':rect.getInfo()['coordinates']})
        print('{}, Downloading: {}, {}'.format(datetime.datetime.now(), lat, lon))
        
        # Fetch data
        img_data = requests.get(path).content
        with open('zipfile/' + str(lat) + '_' + str(lon) + '.zip', 'wb') as handler:
          print('Done. Processing files...')
          handler.write(img_data)
          handler.close()
          zip_ref = zipfile.ZipFile('zipfile/' + str(lat) + '_' + str(lon) + '.zip', 'r')
          zip_ref.extractall('./zipfile')
          zip_ref.close()
        img_data = requests.get(path2).content
        with open('zipfile/' + str(lat) + '_' + str(lon) + '_N.zip', 'wb') as handler:
          print('Done. Processing files...')
          handler.write(img_data)
          handler.close()
          zip_ref = zipfile.ZipFile('zipfile/' + str(lat) + '_' + str(lon) + '_N.zip', 'r')
          zip_ref.extractall('./zipfile')
          zip_ref.close()
        
        # Process unzipped single channel data, RGB data are put together
        files = os.listdir('./zipfile')
        is_image_RGB = None
        for file in files:
          file_n = os.path.join('./zipfile', file)
          if file_n[-4:] == '.tif':
            image = np.asarray(Image.open(file_n))
            H, W = image.shape[0], image.shape[1]
            if not is_image_RGB:
              image_RGB = np.zeros([H, W, 3])
              is_image_RGB = True
            H0, W0, _ = image_RGB.shape
            H, W = np.minimum(H, H0), np.minimum(W, W0)
            if file_n[-5] == 'R':
              image_RGB[:H, :W, 0] = image[:H, :W]
            elif file_n[-5] == 'G':
              image_RGB[:H, :W, 1] = image[:H, :W]
            elif file_n[-5] == 'B':
              image_RGB[:H, :W, 2] = image[:H, :W]
            elif file_n[-5] == 'N':
              ihandle = Image.fromarray(image[:H, :W].astype(np.uint8))
              ihandle.save(os.path.join('./', str(lat) + '_' + str(lon) + '_N.png'))

          # Downloaded files are treated as temp files and removed to save disk
          os.remove(file_n)

        ihandle = Image.fromarray(image_RGB.astype(np.uint8))
        ihandle.save(os.path.join('./', str(lat) + '_' + str(lon) + '.png'))