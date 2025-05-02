import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from browser_use import Agent, Browser, BrowserConfig
from langchain_google_genai import ChatGoogleGenerativeAI

from event_relevance_calculator import calculate_event_relevance
from extract_event_details import extract_event_details
from disqualify_event import EventDisqualifier
from scrap_web_page import scrap_page
from typings import UserProfile

load_dotenv()

model = ChatOllama(model="gemma3:12b")
premium_model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp',
    api_key=os.environ["GEMINI_API_KEY"]
)

# Verify the model is working before proceeding
try:
    premium_model.invoke("Hello")
    print("Google Generative AI is working")
except Exception as e:
    print(f"Error connecting to Google Generative AI: {e}")
    # Fallback to local model if Google API fails
    premium_model = model  # Use the already defined Ollama model as fallback

browser = Browser(
    config=BrowserConfig(
        browser_binary_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    )
)

task = """
    - Go to https://www.eventbrite.com/
    - Enter London as the location
    - Enter the following search query: 'tech'
    - Click on the search button. Note that the search button might be an icon
    - Wait for the events to load
    - A new page will load
    - Scroll passed the promoted events
    - Open the first 5 events
    - Terminate the browser after you visit the first 5 events
"""

# We'll create the agent inside the main function to properly await it
async def main():
    # Initialize the agent
    agent = Agent(
        task=task,
        llm=premium_model,
        browser=browser,
    )
    
    # Run the agent
    results = await agent.run()
    print(f"\nResults from agent:\n{results.urls()}")
    
    # Wait for user input before closing
    input('Press Enter to close the browser...')
    await browser.close()

if __name__ == '__main__':
    asyncio.run(main())

# event_links = [
#     "https://www.eventbrite.co.uk/e/business-networking-in-essex-tickets-1301259966589?aff=ebdssbdestsearch&_gl=1*5o5bu2*_up*MQ..*_ga*MTI5NDQ0MzkxMy4xNzQ1MzM3Mjgx*_ga_TQVES5V6SH*MTc0NTMzNzI4MC4xLjAuMTc0NTMzNzI4MC4wLjAuMA..",
#     "https://www.meetup.com/london-social-circle-over-50s-by-okgather/events/307360394/?eventOrigin=city_most_popular_event",
#     "https://www.meetup.com/meetup-group-rovccswt/events/307324609/?eventOrigin=city_most_popular_event",
#     "https://www.meetup.com/london-meetups/events/306773824/?eventOrigin=city_most_popular_event",
#     "https://www.meetup.com/scenic-london-walking-group/events/307127607/?eventOrigin=city_most_popular_event",
#     "https://www.meetup.com/socialisingeverybodywelcome/events/305289124/?eventOrigin=city_most_popular_event"
# ]

# user_profile: UserProfile = {
#         "age": 28,
#         "gender": "male",
#         "sexual_orientation": "straight",
#         "relationship_status": "in a relationship",
#         "willingness_to_pay": True,
#         "budget": 20,
#         "willingness_for_online": False,
#         "excluded_times": ["after 22:00", "before 9:00", "9-5 weekdays"],
#         "location": "London, UK",
#         "distance_threshold": 10,
#         "time_commitment_in_minutes": 240, # 4 hours
#         "timeframe": {
#             "start_date": datetime(2025, 4, 1),
#             "end_date": datetime(2025, 5, 31)
#         },
#         "interests": ["technology", "coding", "startups", "business", "entrepreneurship", "Formula 1", "motorsports", "go karting", "football", "health", "fitness", "hiking", "nature", "outdoors", "latin dancing", "alcohol free", "offline", "architecture", "interior design"],
#         "goals": ["network professionally", "make new friends", "find a business partner"],
#         "occupation": "software engineer"
#     }

# event_disqualifier = EventDisqualifier(user_profile, model)

# def check_event(event_link: str):
#     print(f"Checking event: {event_link}")

#     webpage_content = scrap_page(event_link)

#     event_details = extract_event_details(webpage_content, model)

#     is_compatible = event_disqualifier.check_compatibility(event_details)

#     if is_compatible:
#         event_relevance = calculate_event_relevance(webpage_content, user_profile, model)
#         print(event_relevance)
#     else:
#         print("Event is not compatible with the user's profile and/or preferences.")

#     print("--------------------------------")

# for event_link in event_links:
#     try:
#         check_event(event_link)
#     except Exception as e:
#         print(f"Error checking event: {e}")
