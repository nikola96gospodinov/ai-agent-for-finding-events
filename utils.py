import requests

def remove_duplicates_based_on_title(events: list[dict]) -> list[dict]:
    unique_events = []
    seen_titles = set()
    for event in events:
        if event["title"] not in seen_titles:
            unique_events.append(event)
            seen_titles.add(event["title"])

    return unique_events

def get_address_coordinates(address: str) -> tuple[float, float] | None:
    url = f"https://nominatim.openstreetmap.org/search?q={address.replace(' ', '+')}&format=json&polygon_kml=1&addressdetails=1"
    headers = {
        'User-Agent': 'EventDisqualifierApp/1.0',  # Required by Nominatim's usage policy
    }
    try:
        result = requests.get(url=url, headers=headers)
        if result.text.strip():
            result_json = result.json()
            if result_json and len(result_json) > 0:
                lat = float(result_json[0]['lat'])
                lon = float(result_json[0]['lon'])
                return (lat, lon)
            else:
                print("No results found in the response")
        else:
            print("Empty response received")
        return None
    except Exception as e:
        print(f"Error getting address coordinates: {e}")
        print(f"Error type: {type(e)}")
        return None