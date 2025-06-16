import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

from app.services.event_processing.event_relevance_calculator import EventRelevanceCalculator
from app.services.event_processing.extract_event_details import extract_event_details
from app.services.event_processing.disqualify_event import EventDisqualifier
from app.services.scraping.scrap_web_page import scrap_page
from app.services.scraping.scrapers import get_event_links
from app.services.event_processing.get_search_keywords_for_event_sites import get_search_keywords_for_event_sites
from app.utils.utils import remove_duplicates_based_on_title, remove_events_with_negative_relevance
from app.services.avatars import user_profile_main, user_profile_creative, user_profile_sports, user_profile_family, user_profile_student, user_profile_main_other

if os.path.exists('.env'):
    load_dotenv(find_dotenv(), override=True)

local_model = ChatOllama(model="gemma3:12b", temperature=0.0)
great_free_model = ChatGoogleGenerativeAI(
    model='gemma-3-27b-it',
    api_key=os.environ["GEMINI_API_KEY"], # type: ignore
    temperature=0.0 
)
powerful_model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash',
    api_key=os.environ["GEMINI_API_KEY"], # type: ignore
    temperature=0.0
)

# Verify the model is working before proceeding
try:
    powerful_model.invoke("Hello")
    print("Google Generative AI is working")
except Exception as e:
    print(f"Error connecting to Google Generative AI: {e}")
    # Fallback to local model if Google API fails
    powerful_model = local_model

search_keywords = get_search_keywords_for_event_sites(user_profile_main, great_free_model)

event_disqualifier = EventDisqualifier(user_profile_main)
event_relevance_calculator = EventRelevanceCalculator(great_free_model, user_profile_main)

async def check_event(event_link: str):
    print(f"Checking event: {event_link}")

    webpage_content = await scrap_page(event_link)

    event_details = extract_event_details(webpage_content, great_free_model)
    
    if event_details is None:
        print("Something went wrong while extracting event details.")
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
    events = remove_events_with_negative_relevance(events)
    
    for event in events:
        print(f"Event: {event['title']} - Link: {event['event_link']} - Relevance: {event['relevance']}\n")

if __name__ == "__main__":
    asyncio.run(main())
