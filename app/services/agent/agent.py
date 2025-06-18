from playwright.async_api import async_playwright

from app.services.event_processing.event_relevance_calculator import EventRelevanceCalculator
from app.services.event_processing.disqualify_event import EventDisqualifier
from app.services.scraping.scrapers import get_event_links
from app.services.event_processing.get_search_keywords_for_event_sites import get_search_keywords_for_event_sites
from app.utils.event_utils import remove_duplicates_based_on_title, remove_events_with_negative_relevance
from app.services.event_processing.check_event import check_event
from app.llm.llm import great_free_model, powerful_model
from app.models.user_profile_model import UserProfile

async def agent(user_profile: UserProfile):
    search_keywords = get_search_keywords_for_event_sites(user_profile, powerful_model)
    event_disqualifier = EventDisqualifier(user_profile)
    event_relevance_calculator = EventRelevanceCalculator(powerful_model, user_profile)

    event_links = await get_event_links(search_keywords)

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)

    events = []
    for event_link in event_links:
        try:
            event = await check_event(event_link, event_disqualifier, event_relevance_calculator, powerful_model, browser)
            if event is not None:
                events.append(event)
        except Exception as e:
            print(f"Error checking event: {e}")
    
    await browser.close()
    await playwright.stop()

    events = sorted(events, key=lambda x: x["relevance"], reverse=True)
    events = remove_duplicates_based_on_title(events)
    events = remove_events_with_negative_relevance(events)
    
    for event in events:
        print(f"Event: {event['title']} - Link: {event['event_link']} - Relevance: {event['relevance']}\n")