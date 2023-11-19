from abc import ABC, abstractmethod

import aiohttp
import asyncio
from src.utils import logger


class BaseCaptchaDecoder(ABC):
    @staticmethod
    async def get_bytes_from_captcha_url(captcha_img_url: str) -> bytes | None:
        """ Получает байты изображения с капчей из переданной ссылки"""
        async with aiohttp.ClientSession() as session:
            async with session.get(captcha_img_url) as response:
                return await response.read()

    @abstractmethod
    async def get_captcha_key(self, captcha_img: bytes):
        """ Возвращает разгаданную каптчу """
        pass


class RuCaptchaDecoder(BaseCaptchaDecoder):
    in_url = 'https://rucaptcha.com/in.php'
    res_url = 'https://rucaptcha.com/res.php'

    def __init__(self, rucaptcha_token: str):
        self._token = rucaptcha_token

    async def __send_decode_request(self, captcha_bytes: bytes) -> int:
        """ Отправляет запрос на расшифровку капчи """
        in_data = {
            'key': self._token,
            'method': 'post',
            'file': captcha_bytes,
            'regsense': '0',
            'numeric': '4',
            'json': '1',
        }

        # Отправляем запрос на расшифровку капчи
        async with aiohttp.ClientSession() as session:
            async with session.post(self.in_url, data=in_data) as response:
                res = await response.json()
        return res.get('request')

    async def __get_decoding_result(self, requested_captcha_id: int) -> str | None:
        """ Получает результат расшифровки ранее отправленной капчи """
        res_data = {
            'key': self._token,
            'action': 'get',
            'id': requested_captcha_id,
            'json': '1',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.res_url, params=res_data) as response:
                res = await response.json()

        return res.get('request')

    async def get_captcha_key(self, captcha_bytes: bytes) -> str | None:
        requested_captcha_id = await self.__send_decode_request(captcha_bytes=captcha_bytes)

        for _ in range(3):
            await asyncio.sleep(10)
            result = await self.__get_decoding_result(requested_captcha_id=requested_captcha_id)
            if result:
                logger.warning('Запрос на капчу был решён')
                return result
