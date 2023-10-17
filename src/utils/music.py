import re
from dataclasses import dataclass
from typing import List, Optional

import urllib.parse

import aiohttp
from bs4 import BeautifulSoup


@dataclass
class Song:
    title: str
    artist: str
    duration: str
    url: str
    cover: Optional[str]
    id: int = 0


# class Music:
#     BASE_URL = 'https://eu.hitmotop.com'
#     HTTP_SUCCESS_CODE = 200
#
#     @classmethod
#     async def get_by_id(cls, song_id: int) -> Song | None:
#         uri = f'{cls.BASE_URL}/song/{song_id}'
#         response = await cls.make_request(uri)
#
#         if response.status != cls.HTTP_SUCCESS_CODE:
#             return None
#
#         soup = BeautifulSoup(await response.text(), 'html.parser')
#         item = soup.find('div', class_='track__info')
#
#         cover = item.parent.find(class_='track__img').get('style')
#         url_match = re.search(r"url\('([^']+)'\)", cover)
#         cover_url = url_match.group(1)
#
#         l_info = item.find(class_='track__info-l')
#         title = l_info.find(class_='track__title').text.strip()
#         artist = l_info.find(class_='track__desc').text.strip()
#
#         r_info = item.find(class_='track__info-r')
#         duration = r_info.find(class_='track__fulltime').text.strip()
#         download_url = r_info.find(class_='track__download-btn')['href']
#         print('песня получена')
#         return Song(id=song_id, title=title, url=download_url, artist=artist, duration=duration, cover=cover_url)
#
#     @classmethod
#     async def search(cls, query: str, count: int = 10, offset: int = 0) -> List[Song]:
#         encoded_query = cls.__encode_text(query)
#         uri = f"{cls.BASE_URL}/search?q={encoded_query}"
#         response = await cls.make_request(uri)
#         songs = await cls.__scratch_songs_from_html(response, count, offset)
#         return songs
#
#     @classmethod
#     async def get_popular(cls, count: int = 10, offset: int = 0) -> List[Song]:
#         uri = f'{cls.BASE_URL}/songs/top-today'
#         response = await cls.make_request(uri)
#         songs = await cls.__scratch_songs_from_html(response, count, offset)
#         return songs
#
#     @classmethod
#     async def get_new(cls, count: int = 10, offset: int = 0) -> List[Song]:
#         uri = f'{cls.BASE_URL}/songs/new'
#         response = await cls.make_request(uri)
#         songs = await cls.__scratch_songs_from_html(response, count, offset)
#         return songs
#
#     @staticmethod
#     def __encode_text(text: str):
#         return urllib.parse.quote(text)
#
#     @staticmethod
#     async def make_request(url: str):
#         async with aiohttp.ClientSession() as session:
#             response = await session.get(url)
#             return response
#
#     @classmethod
#     def __parse_song(cls, item) -> Song:
#         l_info = item.find(class_='track__info-l')
#         song_id = int(l_info['href'].replace('/song/', ''))
#         title = l_info.find(class_='track__title').text.strip()
#         artist = l_info.find(class_='track__desc').text.strip()
#
#         r_info = item.find(class_='track__info-r')
#         duration = r_info.find(class_='track__fulltime').text.strip()
#         download_url = r_info.find(class_='track__download-btn')['href']
#
#         return Song(id=song_id, title=title, url=download_url, artist=artist, duration=duration, cover=None)
#
#     @classmethod
#     async def __scratch_songs_from_html(cls, response: aiohttp.ClientResponse, count: int, offset: int) -> List[Song]:
#         soup = BeautifulSoup(await response.text(), 'html.parser')
#         items = soup.find_all('div', class_='track__info')
#         return [cls.__parse_song(item) for item in items[offset:offset+count]]


import requests


class MusicSync:
    BASE_URL = 'https://eu.hitmotop.com'
    HTTP_SUCCESS_CODE = 200

    @classmethod
    def get_by_id(cls, song_id: int) -> Song | None:
        uri = f'{cls.BASE_URL}/song/{song_id}'
        response = requests.get(uri)

        if response.status_code != cls.HTTP_SUCCESS_CODE:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        item = soup.find('div', class_='track__info')

        cover = item.parent.find(class_='track__img').get('style')
        url_match = re.search(r"url\('([^']+)'\)", cover)
        cover_url = url_match.group(1)

        l_info = item.find(class_='track__info-l')
        title = l_info.find(class_='track__title').text.strip()
        artist = l_info.find(class_='track__desc').text.strip()

        r_info = item.find(class_='track__info-r')
        duration = r_info.find(class_='track__fulltime').text.strip()
        download_url = r_info.find(class_='track__download-btn')['href']
        print('песня получена')
        return Song(id=song_id, title=title, url=download_url, artist=artist, duration=duration, cover=cover_url)

    @classmethod
    def search(cls, query: str, count: int = 10, offset: int = 0) -> List[Song]:
        encoded_query = cls.__encode_text(query)
        uri = f"{cls.BASE_URL}/search?q={encoded_query}"
        response = requests.get(uri)
        songs = cls.__scratch_songs_from_html(response, count, offset)
        return songs

    @classmethod
    def get_popular(cls, count: int = 10, offset: int = 0) -> List[Song]:
        uri = f'{cls.BASE_URL}/songs/top-today'
        response = requests.get(uri)
        songs = cls.__scratch_songs_from_html(response, count, offset)
        return songs

    @classmethod
    def get_new(cls, count: int = 10, offset: int = 0) -> List[Song]:
        uri = f'{cls.BASE_URL}/songs/new'
        response = requests.get(uri)
        songs = cls.__scratch_songs_from_html(response, count, offset)
        return songs

    @staticmethod
    def __encode_text(text: str):
        return urllib.parse.quote(text)

    @classmethod
    def __parse_song(cls, item) -> Song:
        l_info = item.find(class_='track__info-l')
        song_id = int(l_info['href'].replace('/song/', ''))
        title = l_info.find(class_='track__title').text.strip()
        artist = l_info.find(class_='track__desc').text.strip()

        r_info = item.find(class_='track__info-r')
        duration = r_info.find(class_='track__fulltime').text.strip()
        download_url = r_info.find(class_='track__download-btn')['href']

        return Song(id=song_id, title=title, url=download_url, artist=artist, duration=duration, cover=None)

    @classmethod
    def __scratch_songs_from_html(cls, response: requests.Response, count: int, offset: int) -> List[Song]:
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('div', class_='track__info')
        return [cls.__parse_song(item) for item in items[offset:offset+count]]
