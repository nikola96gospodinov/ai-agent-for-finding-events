import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv, find_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

from event_relevance_calculator import calculate_event_relevance
from extract_event_details import extract_event_details
from disqualify_event import EventDisqualifier
from scrap_web_page import scrap_page
from typings import UserProfile
from scraper import EventBriteScraper
if os.path.exists('.env'):
    load_dotenv(find_dotenv(), override=True)

fallback_model = ChatOllama(model="gemma3:12b")
model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp',
    api_key=os.environ["GEMINI_API_KEY"]
)

# Verify the model is working before proceeding
try:
    model.invoke("Hello")
    print("Google Generative AI is working")
except Exception as e:
    print(f"Error connecting to Google Generative AI: {e}")
    # Fallback to local model if Google API fails
    model = fallback_model

scraper = EventBriteScraper()

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

async def check_event(event_link: str):
    print(f"Checking event: {event_link}")

    webpage_content = await scrap_page(event_link)

    event_details = extract_event_details(webpage_content, model)

    is_compatible = event_disqualifier.check_compatibility(event_details)

    if is_compatible:
        event_relevance = calculate_event_relevance(webpage_content, user_profile, model)
        print(event_relevance)
    else:
        print("Event is not compatible with the user's profile and/or preferences.")

    print("--------------------------------")

async def main():
    event_links = await scraper.scrape_events_by_keywords(
        country="United Kingdom",
        city="London",
        keywords=["tech", "business networking", "startups"]
    )

    for event_link in event_links:
        try:
            await check_event(event_link)
        except Exception as e:
            print(f"Error checking event: {e}")

if __name__ == "__main__":
    asyncio.run(main())
