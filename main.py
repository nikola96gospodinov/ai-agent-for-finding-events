from datetime import datetime
from langchain_ollama.llms import OllamaLLM

from event_relevance_calculator import calculate_event_relevance
from scrap_web_page import scrap_page
from extract_event_details import extract_event_details
from disqualify_event import EventDisqualifier
from typings import UserProfile

model = OllamaLLM(model="gemma3:12b")

event_links = [
    "https://www.eventbrite.co.uk/e/business-networking-in-essex-tickets-1301259966589?aff=ebdssbdestsearch&_gl=1*5o5bu2*_up*MQ..*_ga*MTI5NDQ0MzkxMy4xNzQ1MzM3Mjgx*_ga_TQVES5V6SH*MTc0NTMzNzI4MC4xLjAuMTc0NTMzNzI4MC4wLjAuMA..",
    "https://www.meetup.com/london-social-circle-over-50s-by-okgather/events/307360394/?eventOrigin=city_most_popular_event",
    "https://www.meetup.com/meetup-group-rovccswt/events/307324609/?eventOrigin=city_most_popular_event",
    "https://www.meetup.com/london-meetups/events/306773824/?eventOrigin=city_most_popular_event",
    "https://www.meetup.com/scenic-london-walking-group/events/307127607/?eventOrigin=city_most_popular_event",
    "https://www.meetup.com/socialisingeverybodywelcome/events/305289124/?eventOrigin=city_most_popular_event"
]

user_profile: UserProfile = {
        "age": 28,
        "gender": "male",
        "sexual_orientation": "straight",
        "relationship_status": "in a relationship",
        "willingness_to_pay": True,
        "budget": 20,
        "willingness_for_online": False,
        "excluded_times": ["after 22:00", "before 9:00", "9-5 weekdays"],
        "location": "London, UK",
        "distance_threshold": 10,
        "time_commitment_in_minutes": 240, # 4 hours
        "timeframe": {
            "start_date": datetime(2025, 4, 1),
            "end_date": datetime(2025, 5, 31)
        },
        "interests": ["technology", "coding", "startups", "business", "entrepreneurship", "Formula 1", "motorsports", "go karting", "football", "health", "fitness", "hiking", "nature", "outdoors", "latin dancing", "alcohol free", "offline", "architecture", "interior design"],
        "goals": ["network professionally", "make new friends", "find a business partner"],
        "occupation": "software engineer"
    }

event_disqualifier = EventDisqualifier(user_profile, model)

def check_event(event_link: str):
    print(f"Checking event: {event_link}")

    webpage_content = scrap_page(event_link)

    event_details = extract_event_details(webpage_content, model)

    is_compatible = event_disqualifier.check_compatibility(event_details)

    if is_compatible:
        event_relevance = calculate_event_relevance(webpage_content, user_profile, model)
        print(event_relevance)
    else:
        print("Event is not compatible with the user's profile and/or preferences.")

    print("--------------------------------")

for event_link in event_links:
    try:
        check_event(event_link)
    except Exception as e:
        print(f"Error checking event: {e}")
