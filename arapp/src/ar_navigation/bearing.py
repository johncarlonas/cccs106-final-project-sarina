
import math

def bearing_to_target(lat1, lon1, lat2, lon2):
    # Returns bearing from (lat1,lon1) to (lat2,lon2) in degrees (0 = N, 90 = E)
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    initial = math.atan2(x, y)
    initial = math.degrees(initial)
    return (initial + 360) % 360