
import openrouteservice
from openrouteservice import convert
from simplification.cutil import simplify_coords

# ors api key
client = openrouteservice.Client(key="ORS_KEY")

def get_route(start, end, simplify_tol=0.00005):
    # (lat, lon)
    coords = ((start[1], start[0]), (end[1], end[0]))  # (lon, lat)

    # call ORS
    res = client.directions(coords, profile="foot-walking")

    geometry = res["routes"][0]["geometry"]
    decoded = convert.decode_polyline(geometry)

    full_coords = [(c[1], c[0]) for c in decoded["coordinates"]]  # (lat, lon)

    # convert to lon-lat for simplification
    lonlat = [(c[1], c[0]) for c in full_coords]

    # apply Douglas–Peucker
    simplified_lonlat = simplify_coords(lonlat, simplify_tol)

    # convert back to lat-lon
    simplified_latlon = [(c[1], c[0]) for c in simplified_lonlat]

    return simplified_latlon