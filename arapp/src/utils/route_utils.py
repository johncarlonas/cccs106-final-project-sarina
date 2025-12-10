
def compute_route_distance(route_points):
    from math import radians, sin, cos, sqrt, asin
    
    def haversine_m(a_lat, a_lon, b_lat, b_lon):
        R = 6371000  # Earth radius in meters
        dlat = radians(b_lat - a_lat)
        dlon = radians(b_lon - a_lon)
        a = sin(dlat/2)**2 + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c

    if len(route_points) < 2:
        return 0.0, [0.0]

    cumulative = [0.0]
    total = 0.0

    for i in range(1, len(route_points)):
        dist = haversine_m(
            route_points[i-1][0], route_points[i-1][1],
            route_points[i][0], route_points[i][1]
        )
        total += dist
        cumulative.append(total)

    return total, cumulative