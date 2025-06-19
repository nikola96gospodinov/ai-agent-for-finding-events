import json
from playwright.async_api import Browser

from app.services.event_processing.event_relevance_calculator import EventRelevanceCalculator
from app.services.event_processing.disqualify_event import EventDisqualifier
from app.services.event_processing.extract_event_details import extract_event_details
from app.services.scraping.scrap_web_page import scrap_page
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.redis_client import redis_client
from app.utils.event_utils import get_seconds_until_event
from app.models.events_model import EventResult

async def check_event(event_link: str, event_disqualifier: EventDisqualifier, event_relevance_calculator: EventRelevanceCalculator, model: ChatGoogleGenerativeAI, browser: Browser) -> EventResult | None:
    print(f"Checking event: {event_link}")

    # Try to get cached result
    cache_key = f"event_details:{event_link}"
    cached_result = redis_client.get(cache_key)
    
    webpage_content = await scrap_page(event_link, browser)
    
    if cached_result is not None:
        print("Retrieved event from cache:")
        event_details = json.loads(str(cached_result))
        print(event_details)
    else:
        event_details = extract_event_details(webpage_content, model)

        if event_details is None:
            print("Something went wrong while extracting event details.")
            return None
        else:
            redis_client.setex(
                cache_key,
                get_seconds_until_event(event_details["date_of_event"], event_details["start_time"]),
                json.dumps(event_details)
            )

    is_compatible = event_disqualifier.check_compatibility(event_details)

    if is_compatible:
        event_relevance_score = event_relevance_calculator.calculate_event_relevance_score(webpage_content, event_details)
        print(f"Event relevance score: {event_relevance_score}")
        result = EventResult(
            event_details=event_details,
            event_url=event_link,
            relevance=event_relevance_score
        )
        
        return result
    else:
        print("Event is not compatible with the user's profile and/or preferences.")
        return None