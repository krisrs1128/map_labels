#!/usr/bin/env python

"""
Some utilities for fetching open street map labels.
"""

import cv2
import gdal
import json
import numpy as np
import shapely.geometry


def read_multipolygon(geojson_path, buffer_size=1e-5):
    """
    Reads a geojson and converts the result into a Multipolygon
    """
    geojson = json.load(open(geojson_path, "r"))
    geoms = []
    for feature in geojson["features"]:
        geom = shapely.geometry.shape(feature["geometry"])
        if geom.geom_type != "Polygon":
            geom = geom.buffer(buffer_size)
        geoms.append(geom)

    poly = shapely.ops.cascaded_union(
        shapely.geometry.MultiPolygon(geoms)
    )

    return shapely.geometry.MultiPolygon(geoms)


def im_bounds(path):
    """
    Get the latitude and longitude coordinates for lower right and upper left
    corners of geotiff image
    """
    gdal_obj = gdal.Open(path)
    ulx, xres, xskew, uly, yskew, yres  = gdal_obj.GetGeoTransform()
    lrx = ulx + (gdal_obj.RasterXSize * xres)
    lry = uly + (gdal_obj.RasterYSize * yres)
    return {"lr": [lrx, lry], "ul": [ulx, uly]}


def raster_coords(coords, img_size, bbox):
    """
    Convert original coordinates into indices in an image
    """
    for j in [0, 1]:
        coords[:, j] -= bbox["lr"][j]
        coords[:, j] *= (img_size[j] + 1) / (bbox["ul"][j] - bbox["lr"][j])
        coords[:, j] = img_size[j] - coords[:, j]

    return np.round(coords).astype(np.int32)


def multipoly_contours(polygon_list, img_size, bbox):
    """
    Given a generic polygon, get coordinates for the contours
    """
    if not polygon_list:
        return [], []

    to_ind = lambda x: np.array(list(x)).astype(np.float32)
    perim = [
        raster_coords(to_ind(poly.exterior.coords), img_size, bbox)
        for poly in polygon_list
    ]
    inter = [
        raster_coords(to_ind(poly.coords), img_size, bbox)
        for poly_ex in polygon_list for poly in poly_ex.interiors
    ]

    return perim, inter


def make_mask(contours, img_size, class_id=1):
    """
    Generate a mask, given contours
    """
    perim, inter = contours
    m = np.zeros(img_size, np.uint8)

    if not perim:
        return m

    cv2.fillPoly(m, perim, class_id)
    cv2.fillPoly(m, inter, 0)
    return m
