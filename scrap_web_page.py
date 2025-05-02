from playwright.async_api import async_playwright

async def scrap_page(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(1500)
            content = await page.inner_text("body")
            await browser.close()
            await playwright.stop()
            return content
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                raise
