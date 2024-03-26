from playwright.async_api import async_playwright


async def get_download_link(video_url) -> str:
    loader_url = 'https://savefrom.kim/ru/'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(loader_url)

        url_input = await page.wait_for_selector('input#id_url')
        await url_input.type(text=video_url)

        next_button = await page.query_selector('button#search')
        await next_button.click()

        download_button = await page.wait_for_selector('a.results__btn-download')

        async with page.expect_download() as download_info:
            await download_button.click()
        download = await download_info.value

        await browser.close()

    return download.url


from pytube import YouTube


# def get_download_link(url: str) -> tuple[str | None, str | None]:
#     yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
#
#     video_streams = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc()
#
#     # Выбираем первый видео-стрим с разрешением, которое не превышает 50 МБ
#     max_size_mb = 50
#     selected_stream = None
#
#     for stream in video_streams:
#         if stream.filesize / (1024 * 1024) <= max_size_mb:
#             selected_stream = stream
#             break
#     return (yt.video_id, selected_stream.url) or (None, None)

