# app/utils.py

from math import radians, sin, cos, sqrt, atan2

# --- Simulated Geocoding Data ---
# In a real application, you would use a geocoding API (e.g., from geopy library)
# This is a sample for demonstration.
GEOCODE_DATA = {
    'Alappuzha': (9.4981, 76.3388),
    'Ernakulam': (9.9816, 76.2999),
    'Idukki': (9.8483, 76.9695),
    'Kannur': (11.8745, 75.3704),
    'Kasargod': (12.5123, 74.9876),
    'Kollam': (8.8932, 76.6141),
    'Kottayam': (9.5916, 76.5222),
    'Kozhikode': (11.2588, 75.7804),
    'Malappuram': (11.0538, 76.0736),
    'Palakkad': (10.7867, 76.6548),
    'Pathanamthitta': (9.2647, 76.7870),
    'Thiruvananthapuram': (8.5241, 76.9366),
    'Thrissur': (10.5276, 76.2144),
    'Wayanad': (11.6854, 76.1320),
}

def geocode_location(location_name):
    """
    Simulated geocoding function.
    Returns (latitude, longitude) for a given location name.
    """
    if not location_name:
        return None, None
    
    # Handle sub-locations by taking the main district
    main_district = location_name.split(' - ')[0]
    
    coords = GEOCODE_DATA.get(main_district)
    if coords:
        return coords
    
    return None, None

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points in kilometers
    using the Haversine formula.
    """
    R = 6371  # Radius of Earth in kilometers

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance