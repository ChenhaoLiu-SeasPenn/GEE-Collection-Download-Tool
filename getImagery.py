import ee
import numpy as np
from PIL import Image
import os
import requests
import zipfile
import datetime


ee.Initialize()

def accumluate_images(image, images):
    images.append(image)
    return images

if __name__ == '__main__':
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

    collection = ee.ImageCollection("USDA/NAIP/DOQQ").filter(ee.Filter.date('2017-01-01', '2018-12-31'))
    collection = collection.filterBounds(polygon)
    trueColor = collection.select(['R', 'G', 'B'])
    trueColor = trueColor.mosaic()
    NIR = collection.select(['N'])
    NIR = NIR.mean()
    step_len = 0.05
    for lat in np.arange(-74.7, -80.5, -1 * step_len):
      for lon in np.arange(39.7, 42.3, step_len):
    # for lat in np.arange(-76, -76.2, -1 * step_len):
    #   for lon in np.arange(41, 41.2, step_len):
        rect = ee.Geometry.Polygon([[[lat, lon], [lat, lon+step_len], [lat-step_len, lon+step_len], [lat-step_len, lon]]])
        # collection2 = collection.filterBounds(rect)

        path = trueColor.getDownloadUrl({'scale':1, 'region':rect.getInfo()['coordinates']})
        path2 = NIR.getDownloadUrl({'scale': 1, 'region':rect.getInfo()['coordinates']})
        print('{}, Downloading: {}, {}'.format(datetime.datetime.now(), lat, lon))
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
          os.remove(file_n)
        ihandle = Image.fromarray(image_RGB.astype(np.uint8))
        ihandle.save(os.path.join('./', str(lat) + '_' + str(lon) + '.png'))
    # collection = collection.filterBounds(polygon)
    # collection = collection.mean()
    # trueColor = collection.select(['R', 'G', 'B', 'N'])
    # collectionList = trueColor.toList(trueColor.size())
    # collectionSize = collectionList.size().getInfo()
    # print(collectionSize)
    # for i in xrange(collectionSize):
    #     I_i = ee.Image(collectionList.get(i))
    #     id = I_i.getInfo()['id'].split('/')[-1]
    #     # print(I_i.getInfo()['id'].split('/')[-1])
    #     path = I_i.getDownloadUrl({'scale':1})
    #     print('Downloading: '+ id)
    #     img_data = requests.get(path).content
    #     with open('zipfile/' + id+'.zip', 'wb') as handler:
    #         print('Done. Processing files...')
    #         handler.write(img_data)
    #         handler.close()
    #         zip_ref = zipfile.ZipFile('zipfile/' + id+'.zip', 'r')
    #         zip_ref.extractall('./zipfile')
    #         zip_ref.close()
    #         files = os.listdir('./zipfile')
    #         is_image_RGB = None
    #         for file in files:
    #           file_n = os.path.join('./zipfile', file)
    #           if file_n[-4:] == '.tif':
    #             image = np.asarray(Image.open(file_n))
    #             H, W = image.shape[0], image.shape[1]
    #             if not is_image_RGB:
    #               image_RGB = np.zeros([H, W, 3])
    #               is_image_RGB = True
    #             if file_n[-5] == 'R':
    #               image_RGB[..., 0] = image
    #             elif file_n[-5] == 'G':
    #               image_RGB[..., 1] = image
    #             elif file_n[-5] == 'B':
    #               image_RGB[..., 2] = image
    #             elif file_n[-5] == 'N':
    #               ihandle = Image.fromarray(image.astype(np.uint8))
    #               ihandle.save(os.path.join('./', file[:-4]+'.png'))
    #           os.remove(file_n)
    #         ihandle = Image.fromarray(image_RGB.astype(np.uint8))
    #         ihandle.save(os.path.join('./', id+'.png'))