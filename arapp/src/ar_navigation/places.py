
import osmnx as ox
import json
import os

CACHE = "places_cache.json"

def build_places(place_name="Camarines Sur Polytechnic Colleges"):
    # try cache
    if os.path.exists(CACHE):
        with open(CACHE, "r", encoding="utf-8") as f:
            return json.load(f)

    tags = {"building": True}
    gdf = ox.features_from_place(place_name, tags=tags)

    places = {}
    for idx, row in gdf.iterrows():
        name = row.get("name")
        if isinstance(name, str) and name.strip():
            centroid = row.geometry.centroid
            places[name.strip()] = (round(centroid.y, 6), round(centroid.x, 6))

    # save cache
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, indent=2)

    return places

PLACES = build_places()