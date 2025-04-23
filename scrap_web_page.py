from playwright.sync_api import sync_playwright

def scrap_page(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(1500)
                content = page.inner_text("body")
                browser.close()
                return content
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                raise
