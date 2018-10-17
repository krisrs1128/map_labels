#!/usr/bin/env python

"""
Some variations for labeling images
"""

def drop_polygons(polys, p=0.5):
    """
    Randomly drop a fraction of polygons from a multipoly
    """
    subpolys = []
    for i in range(len(polys)):
        if np.random.random() < p:
            subpolys.append(polys[i])

    return shapely.geometry.MultiPolygon(subpolys)


def polygon_centers(polys, buffer=1e-5):
    """
    Replace a polygon with a small circle at its center
    """
    subpolys = []
    for i in range(len(polys)):
        subpolys.append(polys[i].centroid.buffer(buffer))

    return shapely.geometry.MultiPolygon(subpolys)


def coarsened_labels(mask, stride):
    """
    Return coarse boxes where mask had some positive labels
    """
    indices = []

    m, n = mask.shape
    y_ix = list(range(0, m - 1, stride[0]))
    x_ix = list(range(0, n - 1, stride[1]))
    for i in range(len(y_ix) - 1):
        for j in range(len(x_ix) - 1):
            subwindow = mask[y_ix[i] : y_ix[i + 1], x_ix[j] : x_ix[j + 1]]
            if np.any(subwindow == 1):
                indices.append([
                    list(range(y_ix[i], y_ix[i + 1])),
                    list(range(x_ix[j], x_ix[j + 1]))
                ])

    return indices


def coarsened_image(im_shape, indices):
    """
    Version of labels we could get if just asked along a grid
    """
    mask = np.zeros(im_shape)
    for i in range(len(indices)):
        mask[np.ix_(indices[i][0], indices[i][1])] = 1

    return mask
