from playwright.async_api import async_playwright, Browser

async def scrap_page(url, browser: Browser | None = None, max_retries=3):
    created_browser = False
    playwright = None
    for attempt in range(max_retries):
        try:
            if browser is None:
                playwright = await async_playwright().start()
                browser = await playwright.chromium.launch(headless=True)
                created_browser = True

            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(1500)
            content = await page.inner_text("body")
            await page.close()
            if created_browser:
                if browser is not None:
                    await browser.close()
                if playwright is not None:
                    await playwright.stop()
            return content
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                if created_browser:
                    if browser is not None:
                        await browser.close()
                    if playwright is not None:
                        await playwright.stop()
                raise