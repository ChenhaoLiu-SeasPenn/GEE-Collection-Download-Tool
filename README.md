# GEE-Collection-Download-Tool
I found it hard to handle and export large landsat datasets using Google Earth Engine Code Editor, especially when people are unfamiliar with Javascript language. This is a Python-based tool made to download GEE landsat images to local machines. 

## Prerequisites
Google Earth Engine's Python API could be configured using [this tutorial](https://developers.google.com/earth-engine/python_install_manual)

Other prerequisite packages:
```
NumPy
PILLOW
request
```

## Run
To test code, simply run
```
python getImagery.py
``` 

Datasets, areas, filters and channels could be changed at the beginning of the script. User-friendly APIs will be updated in future updates.

## Advantages

This tool:

1) is friendly to non-Javascript users;
2) avoids using of online GEE Code Editor and could be executed in background / on servers;
3) runs several times faster using Python ```request()``` instead of ```Export.image.toDrive()``` (will support bith in the future);
4) is more friendly for those who want to process landsat data with tools not provided by GEE package (like Deep Neural Networks) and prefer to have data on their own disks.

## Author

[Chenhao Liu](https://www.github.com//ChenhaoLiu-SeasPenn)