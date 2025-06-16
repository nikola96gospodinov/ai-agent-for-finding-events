from app.services.event_processing.event_relevance_calculator import EventRelevanceCalculator
from app.services.event_processing.disqualify_event import EventDisqualifier
from app.services.event_processing.extract_event_details import extract_event_details
from app.services.scraping.scrap_web_page import scrap_page
from langchain_google_genai import ChatGoogleGenerativeAI

async def check_event(event_link: str, event_disqualifier: EventDisqualifier, event_relevance_calculator: EventRelevanceCalculator, model: ChatGoogleGenerativeAI):
    print(f"Checking event: {event_link}")

    webpage_content = await scrap_page(event_link)

    event_details = extract_event_details(webpage_content, model)
    
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