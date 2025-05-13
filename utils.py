import requests
import math

from custom_typings import Location, DistanceUnit

def remove_duplicates_based_on_title(events: list[dict]) -> list[dict]:
    unique_events = []
    seen_titles = set()
    for event in events:
        if event["title"] not in seen_titles:
            unique_events.append(event)
            seen_titles.add(event["title"])

    return unique_events

def get_address_coordinates(address: str) -> Location | None:
    url = f"https://nominatim.openstreetmap.org/search?q={address.replace(' ', '+')}&format=json&polygon_kml=1&addressdetails=1"
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
                print("No results found in the response")
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
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(loc1["latitude"])
    lon1_rad = math.radians(loc1["longitude"])
    lat2_rad = math.radians(loc2["latitude"])
    lon2_rad = math.radians(loc2["longitude"])
    
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
