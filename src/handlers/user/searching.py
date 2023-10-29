from aiogram import Dispatcher, Bot
from aiogram.types import Message, InputFile

from config import Config
from src.filters import IsSubscriberFilter
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
# from src.utils.tiktok_api import trending_videos
from src.utils import shazam_api
from src.utils.tiktok_api import get_video
from src.utils.vk_music_api import VkMusicApi


# region Utils
async def __get_media_file_url(bot: Bot, message: Message) -> str | None:
    bot_token = Config.BOT_TOKEN
    media = None

    if message.voice:
        media = message.voice
    elif message.audio:
        media = message.audio
    elif message.video_note:
        media = message.video_note
    elif message.video:
        media = message.video

    if media:
        file = await bot.get_file(media.file_id)
        return f'https://api.telegram.org/file/bot{bot_token}/{file.file_path}'
    return None


# endregion

# region Handlers

async def handle_text_message(message: Message):
    await message.answer_chat_action(action='typing')
    songs = await VkMusicApi.get_songs_by_text(text=message.text, count=8)

    if not songs:
        await message.answer(text=UserMessages.get_song_not_found_error(), parse_mode='HTML')
        return

    markup = UserKeyboards.get_found_songs(songs, current_page_num=1, max_pages=12)
    await message.answer(message.text, reply_markup=markup)


# РЕФАКТОР!
async def handle_media_message(message: Message):
    timer_msg = await message.answer('⏳')
    file_url = await __get_media_file_url(message.bot, message)
    # if not file_url: return

    try:
        song_data = await shazam_api.recognize_song(file_url=file_url)
        cover = InputFile.from_url(url=song_data.photo_url, filename=f'{song_data.title}')
    except Exception as e:
        print(e)
        await message.answer(text=UserMessages.get_song_not_found_error(), parse_mode='HTML')
        await timer_msg.delete()
        return

    songs = await VkMusicApi.get_songs_by_text(text=f'{song_data.title} {song_data.subtitle}', count=5)
    markup = UserKeyboards.get_found_songs(songs, current_page_num=1, append_navigation=False)
    text = UserMessages.get_song_info(song_title=song_data.title, author_name=song_data.subtitle)

    await message.answer_photo(
        photo=cover,
        reply_markup=markup,
        caption=text,
        parse_mode='HTML'
    )
    await timer_msg.delete()


async def handle_youtube_link(message: Message):
    await message.answer('К сожалению, я пока что не умею обрабатывать ссылки на ютуб 😟')


async def handle_tik_tok_link(message: Message):
    await message.answer('К сожалению, я пока что не умею обрабатывать ссылки на TikTok 😟')
    # video_path = await get_video(message.text)
    # video_file = InputFile(video_path)
    # await message.answer_video(video_file)


# endregion


def register_searching_handlers(dp: Dispatcher):
    # ссылка на ютуб
    dp.register_message_handler(
        handle_youtube_link, IsSubscriberFilter(),
        lambda message: 'https://youtu.be/' in message.text or 'https://www.youtube.com/' in message.text
    )

    # ссылка на тик ток
    dp.register_message_handler(
        handle_tik_tok_link, IsSubscriberFilter(),
        lambda message: 'https://www.tiktok.com/' in message.text
    )

    # поиск по тексту
    dp.register_message_handler(handle_text_message, IsSubscriberFilter(), content_types=['text'])

    # кружок / аудио / голосовое / видео
    dp.register_message_handler(
        handle_media_message, IsSubscriberFilter(), content_types=['video_note', 'audio', 'voice', 'video']
    )
