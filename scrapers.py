import asyncio
from playwright.async_api import async_playwright
from typing import List, Optional

class BaseEventScraper:
    """Base class for event scrapers with common functionality."""
    
    def __init__(self, base_url: str, headless: bool = True):
        self.base_url = base_url
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    async def setup(self):
        """Initialize playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
    
    async def close(self):
        """Close browser and playwright."""
        await self.browser.close()
        await self.playwright.stop()
    
    async def extract_event_urls(self, **kwargs):
        """
        Extract URLs of events. To be implemented by subclasses.
        
        Returns:
            List of event URLs
        """
        raise NotImplementedError("Subclasses must implement extract_event_urls")
    
    async def scrape_events_by_keywords(self, keywords: Optional[List[str]] = None, **kwargs):
        """
        Scrape event URLs for multiple keywords.
        
        Args:
            keywords: List of keywords to search for
            **kwargs: Additional keyword arguments for extract_event_urls
            
        Returns:
            List of all event URLs from all keywords combined
        """
        if keywords is None:
            keywords = ["tech", "business", "networking"]
        
        await self.setup()
        all_events = []
        
        try:
            for keyword in keywords:
                print(f"Searching for '{keyword}' events...")
                events = await self.extract_event_urls(keywords=keyword, **kwargs)
                all_events.extend(events)
        finally:
            await self.close()
        
        # Remove duplicates while preserving order
        unique_events = list(dict.fromkeys(all_events))
        return unique_events


class EventBriteScraper(BaseEventScraper):
    def __init__(self, headless: bool = True):
        super().__init__(base_url="https://www.eventbrite.com", headless=headless)
    
    async def extract_event_urls(self, country="United Kingdom", city="London", keywords="tech", promoted_count=2, regular_count=3, **kwargs):
        """
        Extract URLs of events from Eventbrite, separately for promoted and non-promoted events.
        
        Args:
            country: Country to search in
            city: City to search in
            keywords: Search terms to find relevant events
            promoted_count: Number of promoted events to extract
            regular_count: Number of regular (non-promoted) events to extract
            
        Returns:
            List of event URLs
        """
        search_url = f"{self.base_url}/d/{country.lower()}--{city.lower()}/{keywords}/?q={keywords}"
        
        await self.page.goto(search_url)
        
        await self.page.wait_for_selector('ul[class*="SearchResultPanelContentEventCardList-module__eventList"]', timeout=5000)
        
        await asyncio.sleep(1)
        
        for _ in range(2):
            await self.page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(1)
        
        events = []
        
        all_event_cards = await self.page.query_selector_all('ul[class*="SearchResultPanelContentEventCardList-module__eventList"] li')
        
        # Process promoted events
        count = 0
        for card in all_event_cards:
            if count >= promoted_count:
                break
                
            try:
                is_promoted = await card.query_selector('p:has-text("Promoted")')
                if not is_promoted:
                    continue
                
                link_element = await card.query_selector('a[href*="/e/"]')
                if not link_element:
                    continue
                    
                event_url = await link_element.get_attribute('href')
                
                events.append(event_url)

                count += 1
                
            except Exception as e:
                print(f"Error extracting promoted event: {e}")

        # Process regular events
        count = 0
        for card in all_event_cards:
            if count >= regular_count:
                break
                
            try:
                is_promoted = await card.query_selector('p:has-text("Promoted")')
                if is_promoted:
                    continue
                
                link_element = await card.query_selector('a[href*="/e/"]')
                if not link_element:
                    continue
                    
                event_url = await link_element.get_attribute('href')
                
                events.append(event_url)
                
                count += 1
                
            except Exception as e:
                print(f"Error extracting regular event: {e}")

        return events


class MeetupScraper(BaseEventScraper):
    def __init__(self, headless: bool = True):
        super().__init__(base_url="https://www.meetup.com", headless=headless)
    
    async def extract_event_urls(self, location="London", country_code="gb", keywords="tech", max_events=5, **kwargs):
        """
        Extract URLs of events from Meetup.
        
        Args:
            location: Location to search in (city, country)
            keywords: Search terms to find relevant events
            max_events: Maximum number of events to extract
            
        Returns:
            List of event URLs
        """
        # Build the search URL
        # Transform keywords by replacing spaces with %20 for URL encoding
        encoded_keywords = keywords.replace(" ", "%20")
        search_url = f"{self.base_url}/find/?keywords={encoded_keywords}&location={country_code}--{location}&source=EVENTS"
        
        print(f"Navigating to: {search_url}")
        await self.page.goto(search_url)
        
        # Wait for the events to load
        await self.page.wait_for_selector('a[href*="/events/"]', timeout=10000)
        
        # Scroll to load more events
        for _ in range(3):
            await self.page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)
        
        # Extract event links
        events = []
        event_cards = await self.page.query_selector_all('a[href*="/events/"]')
        
        for i, card in enumerate(event_cards):
            if i >= max_events:
                break
                
            try:
                event_url = await card.get_attribute('href')
                if event_url and '/events/' in event_url:
                    full_url = event_url if event_url.startswith('http') else f"{self.base_url}{event_url}"
                    events.append(full_url)
            except Exception as e:
                print(f"Error extracting meetup URL: {e}")
        
        return events

class LumaScraper(BaseEventScraper):
    def __init__(self, headless: bool = True):
        super().__init__(base_url="https://lu.ma", headless=headless)
    
    async def extract_event_urls(self, location="london", max_events=25, keywords=None):
        """
        Extract URLs of events from Luma.
        
        Args:
            location: Location to search in (city name)
            keywords: Search terms to find relevant events
            max_events: Maximum number of events to extract
            
        Returns:
            List of event URLs
        """
        search_url = f"{self.base_url}/{location}".lower()

        await self.page.goto(search_url)

        await self.page.wait_for_selector('a[class*="event-link content-link"]', timeout=10000)
        
        # Scroll to load more events
        for _ in range(3):
            await self.page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)
        
        # Extract event links
        events = []
        event_cards = await self.page.query_selector_all('a[class*="event-link content-link"]')
        
        # Skip the first 5 events
        event_cards = event_cards[5:]

        for i, card in enumerate(event_cards):
            if i >= max_events:
                break

            event_url = await card.get_attribute('href')
            events.append(f"https://lu.ma/{event_url}")
        
        return events
        
    async def scrape_events_by_keywords(self, keywords=None, location="london", max_events=25):
        """
        Override the base class method for Luma since we don't use keywords.
        
        Args:
            keywords: Ignored for Luma
            location: Location to search in
            max_events: Maximum number of events to extract
            
        Returns:
            List of event URLs
        """
        # Just use location directly - ignore keywords
        await self.setup()
        
        try:
            events = await self.extract_event_urls(location=location, max_events=max_events)
            return events
        finally:
            await self.close()

async def get_event_links(search_keywords: list[str], eventbrite = True, meetup = True, luma = True) -> list[str]:
    eventbrite_scraper = EventBriteScraper()
    meetup_scraper = MeetupScraper()
    luma_scraper = LumaScraper()

    event_links = []
    
    if eventbrite:
        event_links.extend(await eventbrite_scraper.scrape_events_by_keywords(
            country="United Kingdom",
            city="London",
            keywords=search_keywords
        ))

    if meetup:
        event_links.extend(await meetup_scraper.scrape_events_by_keywords(
            location="London",
            country_code="gb",
            keywords=search_keywords
        ))

    if luma:
        event_links.extend(await luma_scraper.scrape_events_by_keywords(
            location="London",
            max_events=40,
            keywords=search_keywords
        ))

    return event_links