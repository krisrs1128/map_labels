#!/usr/bin/env python

"""
Just trying to orient myself with the raw data
"""

import shapely.geometry
import shapely.ops
import cv2
import json
import tifffile
import gdal

import matplotlib.pyplot as plt
plt.ion()

raw_dir = "/Users/krissankaran/Desktop/map_labels/data/raw/"

# an example raw image
subdir = "AOI_5_Khartoum_Roads_Sample/"
im_path = raw_dir + subdir + "MUL-PanSharpen/MUL-PanSharpen_AOI_5_Khartoum_img194.tif"
im = tifffile.imread(im_path)
plt.imshow(im[:, :, 0])
plt.imshow(im[:, :, 1])
plt.imshow(im[:, :, 4])
plt.imshow(im[:, :, 7])

# let's see the associated deepglobe mask
label_path = raw_dir + subdir + "geojson/spacenetroads/spacenetroads_AOI_5_Khartoum_img194.geojson"
poly = read_multipolygon(label_path, buffer_size=1e-5)
poly = shapely.ops.cascaded_union(poly)

# get coordinates
gdal_obj = gdal.Open(im_path)
ulx, xres, xskew, uly, yskew, yres  = gdal_obj.GetGeoTransform()
lrx = ulx + (gdal_obj.RasterXSize * xres)
lry = uly + (gdal_obj.RasterYSize * yres)

bbox = {
    "max": [lrx, lry],
    "min": [ulx, uly]
}

img_size = im.shape[:-1]
contours = multipoly_contours(poly, img_size, bbox)
y = make_mask(contours, img_size)

plt.ioff()
plt.close()
plt.imshow(im[:, :, 4], alpha=0.9)
plt.imshow(y, alpha=0.2)
plt.show()

# can we now get some analogous labelings from OpenStreetMap?
