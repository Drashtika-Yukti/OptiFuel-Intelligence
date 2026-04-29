import requests
import math
import pandas as pd
import numpy as np
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FuelOptimizer")

class FuelOptimizerError(Exception):
    """Base exception for all optimizer errors"""
    pass

class GeocodingError(FuelOptimizerError):
    """Raised when location lookup fails"""
    pass

class RoutingError(FuelOptimizerError):
    """Raised when routing API fails"""
    pass

try:
    from scipy.spatial import KDTree
    HAS_SCIPY = True
except ImportError:
    logger.warning("scipy not found. Spatial index will use brute-force fallback.")
    HAS_SCIPY = False

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

class SpatialIndex:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        # Drop rows with missing lat/lon
        self.df = self.df.dropna(subset=['lat', 'lon'])
        self.coords = self.df[['lat', 'lon']].values
        if HAS_SCIPY:
            self.tree = KDTree(self.coords)
        else:
            print("WARNING: scipy not found. Using slower brute-force spatial search.")

    def find_nearby_stations(self, lat, lon, radius_miles=5):
        if HAS_SCIPY:
            # Convert miles to rough degrees (1 degree lat ~= 69 miles)
            approx_radius_deg = radius_miles / 69.0
            indices = self.tree.query_ball_point([lat, lon], approx_radius_deg)
            if not indices:
                return []
            nearby = self.df.iloc[indices].copy()
        else:
            # Brute force fallback
            # We filter by a bounding box first for a bit of speed
            lat_deg = radius_miles / 69.0
            lon_deg = radius_miles / (69.0 * math.cos(math.radians(lat)))
            mask = (self.df['lat'] >= lat - lat_deg) & (self.df['lat'] <= lat + lat_deg) & \
                   (self.df['lon'] >= lon - lon_deg) & (self.df['lon'] <= lon + lon_deg)
            nearby = self.df[mask].copy()

        if nearby.empty:
            return []
            
        # Refine with actual Haversine distance
        nearby['distance'] = nearby.apply(lambda row: haversine(lat, lon, row['lat'], row['lon']), axis=1)
        return nearby[nearby['distance'] <= radius_miles].to_dict('records')

def get_route(start_coords, end_coords):
    """
    Calls OSRM public API to get route.
    """
    url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=polyline"
    try:
        logger.info(f"Fetching route from OSRM: {start_coords} -> {end_coords}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data['code'] == 'Ok':
            return data['routes'][0]
        else:
            raise RoutingError(f"OSRM Error: {data['code']}")
    except Exception as e:
        logger.error(f"Routing API failed: {str(e)}")
        raise RoutingError(f"Connection to Routing API failed: {str(e)}")

def geocode(location_name):
    """
    Geocodes location name to lat/lon.
    """
    # Simple dictionary for common US cities
    cities = {
        "New York": (40.7128, -74.0060),
        "Los Angeles": (34.0522, -118.2437),
        "Chicago": (41.8781, -87.6298),
        "Houston": (29.7604, -95.3698),
        "Phoenix": (33.4484, -112.0740),
        "Philadelphia": (39.9526, -75.1652),
        "San Antonio": (29.4241, -98.4936),
        "San Diego": (32.7157, -117.1611),
        "Dallas": (32.7767, -96.7970),
        "San Jose": (37.3382, -121.8863),
    }
    
    clean_name = location_name.split(',')[0].strip()
    if clean_name in cities:
        return cities[clean_name]
    
    try:
        logger.info(f"Geocoding location: {location_name}")
        url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
        headers = {'User-Agent': 'FuelOptimizerApp/1.0'}
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        items = resp.json()
        if items:
            return (float(items[0]['lat']), float(items[0]['lon']))
        raise GeocodingError(f"Location not found: {location_name}")
    except Exception as e:
        logger.error(f"Geocoding failed for {location_name}: {str(e)}")
        raise GeocodingError(f"Geocoding service error: {str(e)}")
