from .pyktok import save_tiktok, specify_browser

# specify_browser('chrome')


async def get_video(url: str):
    save_tiktok(video_url=url, browser_name='chrome')
    print('finish')
    pass
