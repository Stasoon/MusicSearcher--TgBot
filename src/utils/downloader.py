import os.path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor

import yt_dlp
import asyncio

from yt_dlp import DownloadError

from src.utils import logger


class Downloader:

    path = os.path.join('videos', f'{str(uuid4())[:15]}_%(title)s.%(ext)s')
    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
        'outtmpl': path,
        'format': f'18/bv*[height<={720}][ext=mp4]',
    }
    ydl = yt_dlp.YoutubeDL(ydl_opts)

    @staticmethod
    def __get_resolution_and_thumb(info_dict: dict) -> tuple:
        """ Получает разрешение и ссылку на обложку """
        width, height, thumbnail_url = [None] * 3

        if 'formats' in info_dict:
            format_info = info_dict['formats'][-1]
            width, height = format_info.get('width'), format_info.get('height')

        if 'thumbnails' in info_dict and height:
            def is_best_resolution(thumbnail):
                return thumbnail.get('width') is not None and thumbnail.get('height') is not None

            try:
                best_thumbnail = max(
                    filter(is_best_resolution, info_dict['thumbnails']),
                    key=lambda t: t['width'] * t['height'] and t['url'].endswith('.jpg')
                )
                thumbnail_url = best_thumbnail['url'] if best_thumbnail else None
            except ValueError:
                thumbnail_url = info_dict['thumbnails'][-1].get('url')

        return width, height, thumbnail_url

    @classmethod
    def __get_video_info(cls, video_url) -> dict:
        info = cls.ydl.extract_info(video_url, download=False)
        width, height, thumbnail_url = cls.__get_resolution_and_thumb(info)

        return {
            'id': info.get('id'),
            'title': f"{info.get('title')}.mp4",
            'duration': int(info.get('duration')),
            'width': width, 'height': height,
            'thumbnail_url': thumbnail_url
        }

    @classmethod
    async def get_video_info(cls, video_url: str) -> dict | None:
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor()

        try:
            data = await loop.run_in_executor(executor, cls.__get_video_info, video_url)
        except Exception as e:
            logger.error(e)
            data = None

        return data

    @classmethod
    def __save_video(cls, video_url) -> dict:
        with cls.ydl:
            info = cls.ydl.extract_info(video_url, download=True)
            resolution, thumbnail_url = cls.__get_resolution_and_thumb(info)

            return {
                'id': info.get('id'),
                'title': f"{info.get('title')}.mp4",
                'duration': info.get('duration'),
                'file_path': cls.ydl.prepare_filename(info),
                'resolution': resolution,
                'thumbnail_url': thumbnail_url
            }

    @classmethod
    async def save_video(cls, video_url: str) -> dict:
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor()

        try:
            data = await loop.run_in_executor(executor, cls.__save_video, video_url)
        except DownloadError as e:
            logger.error(e)
            data = None
        return data
