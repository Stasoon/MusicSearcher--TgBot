import aiohttp
from bs4 import BeautifulSoup


class ProfileLinkValidator:
    @staticmethod
    def is_profile_link_valid(link: str) -> bool:
        if link.startswith('@') or link.startswith('vk.com/') or link.startswith('https://vk.com/'):
            return True
        else:
            return False

    @staticmethod
    def get_id_from_link(url: str) -> int:
        str_id = url \
            .replace('https://', '') \
            .replace('vk.com/', '') \
            .replace('public', '') \
            .replace('club', '') \
            .replace('id', '')

        str_id = int(str_id)
        if 'club' in url or 'public' in url:
            str_id = f'-{str_id}'
        return int(str_id)

    @staticmethod
    def get_extended_vk_url(short: str) -> str:
        https_str = 'https://'
        vk_domain = 'vk.com/'

        if short.startswith('@'):
            return f'{https_str}{vk_domain}{short[1:]}'
        elif short.startswith(vk_domain):
            return f'{https_str}{short}'
        else:
            return short


class VkProfileParser:
    @classmethod
    async def get_id_and_title_by_profile_link(cls, profile_link: str) -> tuple[int | None, str | None]:
        # Если ссылка передана в сокращённом виде, получаем полную
        page_url = ProfileLinkValidator.get_extended_vk_url(profile_link)

        # Делаем запрос по ссылке
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        headers = {'User-Agent': user_agent}
        async with aiohttp.ClientSession() as session:
            async with session.get(page_url, headers=headers) as response:
                page_html = await response.text()

        parser = BeautifulSoup(page_html, 'html.parser')
        profile_id, profile_title = cls.__fetch_profile_id(parser), cls.__fetch_profile_title(parser)
        return profile_id, profile_title

    @staticmethod
    def __fetch_profile_id(page_parser):
        try:
            # Получаем оригинальный адрес на пользователя
            meta_tag = page_parser.find('meta', {'property': 'og:url'})
            user_url_with_id = meta_tag.get('content')
            # Получаем id профиля из ссылки
            profile_id = ProfileLinkValidator.get_id_from_link(user_url_with_id)
        except Exception as e:
            print(e)
            return None

        if not profile_id:
            return None
        return profile_id

    @staticmethod
    def __fetch_profile_title(page_parser):
        # Получаем имя
        profile_title = page_parser.find('title').get_text().replace('| ВКонтакте', '').strip()
        return profile_title
