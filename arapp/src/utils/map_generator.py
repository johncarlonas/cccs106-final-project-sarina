"""Generate OpenStreetMap HTML with route visualization"""
import os
import json
from datetime import datetime
import folium
from folium import plugins
import io
import base64

def generate_route_map(start_coords, end_coords, route_points):
    """
    Generate an OpenStreetMap HTML with route highlighted
    
    Args:
        start_coords: (lat, lon) of starting location
        end_coords: (lat, lon) of destination
        route_points: list of (lat, lon) tuples representing the route
    
    Returns:
        HTML string for the map
    """
    
    # Convert route points to GeoJSON format for Leaflet
    route_coordinates = "[\n"
    for i, (lat, lon) in enumerate(route_points):
        route_coordinates += f"        [{lon}, {lat}]"
        if i < len(route_points) - 1:
            route_coordinates += ",\n"
        else:
            route_coordinates += "\n"
    route_coordinates += "    ]"
    
    start_lat, start_lon = start_coords
    end_lat, end_lon = end_coords
    
    # Calculate center of map
    center_lat = (start_lat + end_lat) / 2
    center_lon = (start_lon + end_lon) / 2
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Route Map</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f5f5f5;
            }}
            #map {{
                width: 100%;
                height: 100%;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .info-popup {{
                background: white;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            // Initialize map
            const map = L.map('map').setView([{center_lat}, {center_lon}], 15);
            
            // Add OpenStreetMap tiles
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19,
                maxNativeZoom: 18
            }}).addTo(map);
            
            // Add start marker (Green)
            const startMarker = L.circleMarker(
                [{start_lat}, {start_lon}],
                {{
                    radius: 8,
                    fillColor: '#4CAF50',
                    color: '#2E7D32',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }}
            ).addTo(map);
            startMarker.bindPopup('<div class="info-popup"><b>Start Location</b></div>').openPopup();
            
            // Add end marker (Red)
            const endMarker = L.circleMarker(
                [{end_lat}, {end_lon}],
                {{
                    radius: 8,
                    fillColor: '#F44336',
                    color: '#C62828',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }}
            ).addTo(map);
            endMarker.bindPopup('<div class="info-popup"><b>Destination</b></div>');
            
            // Add route as polyline (Blue highlight)
            const routeCoordinates = {route_coordinates};
            const routeLine = L.polyline(routeCoordinates, {{
                color: '#2196F3',
                weight: 4,
                opacity: 0.8,
                lineCap: 'round',
                lineJoin: 'round',
                dashArray: '5, 5'
            }}).addTo(map);
            
            // Add a semi-transparent shadow for better visibility
            const routeShadow = L.polyline(routeCoordinates, {{
                color: '#000000',
                weight: 6,
                opacity: 0.15,
                lineCap: 'round',
                lineJoin: 'round'
            }}).addTo(map);
            
            // Fit map to show entire route
            const group = new L.featureGroup([startMarker, endMarker, routeLine]);
            map.fitBounds(group.getBounds().pad(0.1), {{ animate: true }});
        </script>
    </body>
    </html>
    """
    
    return html


def generate_static_map_image(start_coords, end_coords, route_points, width=400, height=300):
    """
    Generate a static map image using folium
    
    Args:
        start_coords: (lat, lon) of starting location
        end_coords: (lat, lon) of destination
        route_points: list of (lat, lon) tuples representing the route
        width: image width
        height: image height
    
    Returns:
        Base64 encoded PNG image string
    """
    try:
        start_lat, start_lon = start_coords
        end_lat, end_lon = end_coords
        
        # Calculate center
        center_lat = (start_lat + end_lat) / 2
        center_lon = (start_lon + end_lon) / 2
        
        # Create folium map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=15,
            tiles='OpenStreetMap'
        )
        
        # Add route as polyline
        folium.PolyLine(
            locations=route_points,
            color='#2196F3',
            weight=4,
            opacity=0.8,
            popup='Route'
        ).add_to(m)
        
        # Add markers
        folium.CircleMarker(
            location=[start_lat, start_lon],
            radius=8,
            popup='My Location',
            color='#2E7D32',
            fill=True,
            fillColor='#4CAF50',
            fillOpacity=0.8,
            weight=2
        ).add_to(m)
        
        folium.CircleMarker(
            location=[end_lat, end_lon],
            radius=8,
            popup='Destination',
            color='#C62828',
            fill=True,
            fillColor='#F44336',
            fillOpacity=0.8,
            weight=2
        ).add_to(m)
        
        # Save to HTML string
        html_string = m._repr_html_()
        return html_string
        
    except Exception as e:
        print(f"Error generating static map: {e}")
        return None


def save_map_html(html_content, filename=None):
    """
    Save map HTML to a temporary file
    
    Args:
        html_content: HTML string
        filename: optional filename (defaults to timestamp-based name)
    
    Returns:
        Path to the saved HTML file
    """
    if filename is None:
        filename = f"map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    # Get the temp directory - from src/utils go up to arapp, then to storage/temp
    arapp_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    temp_dir = os.path.join(arapp_dir, "storage", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    filepath = os.path.join(temp_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Saved map to: {filepath}")
    return filepath
