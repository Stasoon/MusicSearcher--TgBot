import json
import os
import random
import re
from random import choice

import requests
from pathlib import Path
# import aiohttp
from bs4 import BeautifulSoup
from shazamio.user_agent import USER_AGENTS


headers = {'Accept-Encoding': 'gzip, deflate, sdch',
           'Accept-Language': 'en-US,en;q=0.8',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Cache-Control': 'max-age=0',
           'Connection': 'keep-alive'}
proxies = {
    'http': 'user139226:5ptznc@45.90.197.65:8754'
}
url_regex = '(?<=\.com/)(.+?)(?=\?|$)'
runsb_err = ('No browser defined for cookie extraction. We strongly recommend you run \'specify_browser\', '
             'which takes as its sole argument a string representing a browser installed on your system, e.g. '
             '"chrome," "firefox," "edge," etc.')


with open(Path(__file__).parent / 'tiktok_cookies.json', 'r') as cookie_file:
    cookies = json.load(cookie_file)
cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}


def get_tiktok_data_json(video_url):
    response = requests.get(
        video_url, headers=headers,
        cookies=cookies_dict, timeout=20,
        proxies=proxies
    )
    print(response)
    print(response.cookies)

    # retain any new cookies that got set in this request
    soup = BeautifulSoup(response.text, "html.parser")
    tt_script = soup.find('script', attrs={'id': "SIGI_STATE"})
    try:
        tt_json = json.loads(tt_script.string)
    except AttributeError:
        print(
            "The function encountered a downstream error and did not deliver any data, "
            "which happens periodically for various reasons. Please try again later."
        )
        return

    with open('data.json', 'w') as file:
        file.write(json.dumps(tt_json, indent=4))
        print('json data saved')
    video_id = next(i for i in tt_json['ItemModule'].keys())
    # print(video_id, tt_json['ItemModule'])
    return tt_json['ItemModule'].get(video_id)


def save_tiktok(
        video_url,
        browser_name=None,
        save_path: str = ''
):
    print('start saving')

    tt_json = get_tiktok_data_json(video_url)
    print(tt_json)

    if 'imagePost' in tt_json:
        return

    regex_url = re.findall(url_regex, video_url)[0]
    tt_video_url = tt_json['video']['downloadAddr']
    print(tt_json['music'], f"{tt_json['music']['title']} {tt_json['music']['authorName']}", f"Оригинальное аудио? {tt_json['music']['original']}")
    print('ссылка на аудио', tt_json['music']['playUrl'])

    headers.copy()['referer'] = 'https://www.tiktok.com/'
    headers['User-Agent'] = choice(USER_AGENTS)

    # include cookies with the video request
    tt_video_response = requests.get(tt_video_url, allow_redirects=True, headers=headers, cookies=cookies)
    if tt_video_response.status_code != 200:
        raise Exception(f'Unable to load TikTok video: request status code - {tt_video_response.status_code}')

    video_fn = regex_url.replace('/', '_') + '.mp4'
    with open(video_fn, 'wb') as fn:
        fn.write(tt_video_response.content)
    print('saved')
