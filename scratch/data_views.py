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
im_path = raw_dir + subdir + "MUL-PanSharpen/MUL-PanSharpen_AOI_5_Khartoum_img304.tif"
im = tifffile.imread(im_path)
plt.imshow(im[:, :, 0])
plt.imshow(im[:, :, 1])
plt.imshow(im[:, :, 4])
plt.imshow(im[:, :, 7])

# let's see the associated deepglobe mask
label_path = raw_dir + subdir + "geojson/spacenetroads/spacenetroads_AOI_5_Khartoum_img304.geojson"
poly = read_multipolygon(label_path)

# get coordinates
bbox = im_bounds(im_path)
img_size = im.shape[:-1]
contours = multipoly_contours(poly, img_size, bbox)
y = make_mask(contours, img_size)

plt.ioff()
plt.close()
plt.imshow(im[:, :, 7], alpha=0.9)
plt.imshow(y, alpha=0.2)
plt.show()

# can we now get some analogous labelings from OpenStreetMap?
query_skeleton = "[output:json];({});(._;>;); out;"
bb_string = "{},{},{},{}".format(bbox["lr"][1], bbox["ul"][0], bbox["ul"][1], bbox["lr"][0])
road_query = "way['highway']({});".format(bb_string)
write_geojson_(query_skeleton.format(road_query), "osm_roads")
poly = read_multipolygon("osm_roads.geojson")
contours = multipoly_contours(poly, img_size, bbox)
y = make_mask(contours, img_size)

plt.imshow(im[:, :, 4], alpha=0.9)
plt.imshow(y, alpha=0.2)
plt.show()

# what if we dropped some random number of polygons
subpoly = drop_polygons(poly)
contours = multipoly_contours(subpoly, img_size, bbox)
y = make_mask(contours, img_size)

plt.imshow(im[:, :, 4], alpha=0.9)
plt.imshow(y, alpha=0.2)
plt.show()

# now try coarsening the labels
indices = coarsened_labels(y, [100, 100])
y = coarsened_image(y.shape, indices)

plt.imshow(im[:, :, 4], alpha=0.9)
plt.imshow(y, alpha=0.2)
plt.show()

# alternatively, try extracting just the centers of each polygon
subpoly = polygon_centers(poly)
contours = multipoly_contours(subpoly, img_size, bbox)
y = make_mask(contours, img_size)

plt.imshow(im[:, :, 4], alpha=0.9)
plt.imshow(y, alpha=0.2)
plt.show()
