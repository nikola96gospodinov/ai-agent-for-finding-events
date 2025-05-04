import asyncio
from playwright.async_api import async_playwright
from typing import List
class EventBriteScraper:
    def __init__(self):
        self.base_url = "https://www.eventbrite.com"
        
    async def setup(self):
        """Initialize playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)  # Set to True for production
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
    
    async def close(self):
        """Close browser and playwright."""
        await self.browser.close()
        await self.playwright.stop()
    
    async def extract_event_urls(self, country="United Kingdom", city="London", keywords="tech", promoted_count=2, regular_count=3):
        """
        Extract URLs of events from Eventbrite, separately for promoted and non-promoted events.
        
        Args:
            country: Country to search in
            city: City to search in
            keywords: Search terms to find relevant events
            promoted_count: Number of promoted events to extract
            regular_count: Number of regular (non-promoted) events to extract
            
        Returns:
            Dictionary with lists of promoted and regular event URLs
        """
        search_url = f"{self.base_url}/d/{country.lower()}--{city.lower()}/{keywords}/?q={keywords}"
        
        await self.page.goto(search_url)
        print(f"Navigated to search page: {search_url}")
        
        await self.page.wait_for_selector('ul[class*="SearchResultPanelContentEventCardList-module__eventList"]', timeout=5000)
        print("Found event list container")
        
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

                print(f"Found promoted event {count+1}: {event_url}")
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
                
                print(f"Found regular event {count+1}: {event_url}")
                count += 1
                
            except Exception as e:
                print(f"Error extracting regular event: {e}")

        return events
    
    async def scrape_events_by_keywords(self, country="United Kingdom", city="London", keywords:List[str] | None=None):
        """
        Scrape event URLs for multiple keywords.
        
        Args:
            country: Country to search in
            city: City to search in
            keywords: List of keywords to search for
            
        Returns:
            List of all event URLs from all keywords combined
        """
        if keywords is None:
            keywords = ["tech", "business", "networking"]
        
        await self.setup()
        all_events = []
        
        try:
            for keyword in keywords:
                print(f"\nSearching for '{keyword}' events in {city}...")
                events = await self.extract_event_urls(
                    country=country,
                    city=city,
                    keywords=keyword
                )
                all_events.extend(events)
        finally:
            await self.close()
        
        return all_events
        