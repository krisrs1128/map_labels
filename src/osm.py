#!/usr/bin/env python

"""
Some utilities for getting geojson labels from OSM
"""
import json
import requests

def load_json(query_skeleton, query):
    query_final = query_skeleton.format(query)
    write_geojson_(query_final, "tmp")
    with open("tmp.geojson", "r") as f:
        result = json.load(f)

    os.remove("tmp.geojson")
    return result


def write_geojson_(query_final, fname):
    """
    Internal fun to write a overpass result

    This writes the result of a call to the overpass API, once the query has
    been finalized.
    """
    result = requests.get("http://overpass-api.de/api/interpreter?data={}".format(query_final))
    with open("tmp.json", "w") as f:
        json.dump(result.json(), f)

    os.system("osmtogeojson tmp.json > {}.geojson".format(fname))
    os.remove("tmp.json")
