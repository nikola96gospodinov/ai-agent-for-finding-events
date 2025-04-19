from playwright.sync_api import sync_playwright

def scrap_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        content = page.inner_text("body")
        browser.close()
        return content
