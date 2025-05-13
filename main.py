import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv, find_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

from event_relevance_calculator import EventRelevanceCalculator
from extract_event_details import extract_event_details
from disqualify_event import EventDisqualifier
from scrap_web_page import scrap_page
from custom_typings import UserProfile
from scrapers import get_event_links
from get_search_keywords import get_search_keywords
from utils import remove_duplicates_based_on_title

if os.path.exists('.env'):
    load_dotenv(find_dotenv(), override=True)

# Due to limitations in the Gemini API, we're using exclusively Ollama for now
model = ChatOllama(model="gemma3:12b")
# model = ChatGoogleGenerativeAI(
#     model='gemini-2.0-flash-exp',
#     api_key=os.environ["GEMINI_API_KEY"]
# )

# # Verify the model is working before proceeding
# try:
#     model.invoke("Hello")
#     print("Google Generative AI is working")
# except Exception as e:
#     print(f"Error connecting to Google Generative AI: {e}")
#     # Fallback to local model if Google API fails
#     model = fallback_model



user_profile: UserProfile = {
        "age": 28,
        "gender": "male",
        "sexual_orientation": "straight",
        "relationship_status": "in a relationship",
        "willingness_to_pay": True,
        "budget": 50,
        "willingness_for_online": False,
        "excluded_times": ["after 22:00", "before 9:00", "9-5 weekdays"],
        "location": {
            "latitude": 51.5253263,
            "longitude": -0.1015115
        },
        "distance_threshold": {
            "distance_threshold": 10,
            "unit": "miles"
        },
        "time_commitment_in_minutes": 240, # 4 hours
        "timeframe": {
            "start_date": datetime(2025, 4, 1),
            "end_date": datetime(2025, 12, 31)
        },
        "interests": ["technology", "coding", "startups", "business", "entrepreneurship", "Formula 1", "motorsports", "go karting", "football", "health", "fitness", "hiking", "nature", "outdoors", "latin dancing", "alcohol free", "offline", "architecture", "interior design"],
        "goals": ["network professionally", "make new friends", "find a business partner"],
        "occupation": "software engineer"
    }

search_keywords = get_search_keywords(user_profile, model)
event_disqualifier = EventDisqualifier(user_profile, model)
event_relevance_calculator = EventRelevanceCalculator(model, user_profile)

async def check_event(event_link: str):
    print(f"Checking event: {event_link}")

    webpage_content = await scrap_page(event_link)

    event_details = extract_event_details(webpage_content, model)
    
    if event_details is None:
        print("Event is either sold out or not available.")
        return None

    is_compatible = event_disqualifier.check_compatibility(event_details)

    if is_compatible:
        event_relevance_score = event_relevance_calculator.calculate_event_relevance_score(webpage_content, event_details)
        print(f"Event relevance score: {event_relevance_score}")
        return {
            "event_link": event_link,
            "relevance": event_relevance_score,
            "title": event_details["title"]
        }
    else:
        print("Event is not compatible with the user's profile and/or preferences.")
        return None

async def main():
    event_links = await get_event_links(search_keywords)

    events = []
    for event_link in event_links:
        try:
            event = await check_event(event_link)
            if event is not None:
                events.append(event)
        except Exception as e:
            print(f"Error checking event: {e}")

    events = sorted(events, key=lambda x: x["relevance"], reverse=True)
    events = remove_duplicates_based_on_title(events)
    
    for event in events:
        print(f"Event: {event['title']} - Link: {event['event_link']} - Relevance: {event['relevance']}\n")

if __name__ == "__main__":
    asyncio.run(main())
