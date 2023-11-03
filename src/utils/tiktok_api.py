import aiohttp
from bs4 import BeautifulSoup


async def get_tiktok_download_link(link):
    tmate_url = "https://tmate.cc/"
    headers = {
        'User-Agent': 'ваш User-Agent',
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(tmate_url) as response:
            if response.status != 200:
                return

            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            token = soup.find("input", {"name": "token"})["value"]

        data = {'url': link, 'token': token}

        async with session.post('https://tmate.cc/download', data=data) as response:
            if response.status != 200:
                return

            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            download_link = soup.find(class_="downtmate-right is-desktop-only right").find_all("a")[0]["href"]

    return download_link
