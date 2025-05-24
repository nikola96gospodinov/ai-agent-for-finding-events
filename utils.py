import requests
from urllib.parse import quote
import math
import re

from custom_typings import Location, DistanceUnit

def remove_duplicates_based_on_title(events: list[dict]) -> list[dict]:
    unique_events = []
    seen_titles = set()
    for event in events:
        if event["title"] not in seen_titles:
            unique_events.append(event)
            seen_titles.add(event["title"])

    return unique_events

def extract_postcode_from_address(address: str) -> str | None:
    postcode_pattern = r'\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b'
    match = re.search(postcode_pattern, address)
    return match.group(0) if match else None

def get_address_coordinates(address: str | None) -> Location | None:
    if address is None:
        return None

    url = f"https://nominatim.openstreetmap.org/search?q={quote(address)}&format=json&polygon_kml=1&addressdetails=1"
    headers = {
        'User-Agent': 'EventDisqualifierApp/1.0',  # Required by Nominatim's usage policy
    }
    try:
        result = requests.get(url=url, headers=headers)
        if result.text.strip():
            result_json = result.json()
            if result_json and len(result_json) > 0:
                return {
                    "latitude":  float(result_json[0]['lat']),
                    "longitude": float(result_json[0]['lon'])
                }
            else:
                # Sometimes the address is not found, so we try to extract the postcode and search for that which usually works although it's not as accurate
                postcode = extract_postcode_from_address(address)
                if postcode:
                    url = f"https://nominatim.openstreetmap.org/search?q={quote(postcode)}&format=json&polygon_kml=1&addressdetails=1"
                    result = requests.get(url=url, headers=headers)
                    if result.text.strip():
                        result_json = result.json()
                        if result_json and len(result_json) > 0:
                            return {
                                "latitude":  float(result_json[0]['lat']),
                                "longitude": float(result_json[0]['lon'])
                            }
        else:
            print("Empty response received")
        return None
    except Exception as e:
        print(f"Error getting address coordinates: {e}")
        print(f"Error type: {type(e)}")
        return None

def calculate_distance(loc1: Location, loc2: Location, distance_unit: DistanceUnit) -> float:
    """
    Calculate the distance between two locations using the Haversine formula.
    Returns the distance in kilometers.
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    lat1 = loc1.get("latitude")
    lon1 = loc1.get("longitude")
    lat2 = loc2.get("latitude")
    lon2 = loc2.get("longitude")
    
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')
    
    assert lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    if distance_unit == "km":
        return distance
    else:
        return distance * 0.621371

def get_age_bracket(age: int) -> str:
    decade = (age // 10) * 10

    if age < 20:
        return "teens"
    
    return f"{decade}s"