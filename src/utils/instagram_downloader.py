from playwright.async_api import async_playwright


async def get_instagram_video_download_url(video_url: str) -> str:
    loader_url = 'https://igsaved.com/ru/'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(loader_url)

        await page.wait_for_timeout(500)
        url_input = await page.query_selector('input.search__input.js__search-input')
        await url_input.type(text=video_url)

        next_button = await page.query_selector('button.search__button.search__button_download')
        await next_button.click()

        await page.wait_for_timeout(1500)
        download_button = await page.wait_for_selector('a.button.button__blue')
        download_link = str(await download_button.get_property('href'))

        await browser.close()

    return download_link
