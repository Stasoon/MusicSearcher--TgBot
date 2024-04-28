from src.start_bot import start_bot
from src.utils import setup_logger

# Получение нового токена
# from src.utils.vkpymusic.create_acc import authorize_and_get_token
# authorize_and_get_token(login='87024350146', password='fvuyxuez')

# VkSongCover().make_auth(login='89088252605', password='89088252605iggi')


def main():
    setup_logger()
    start_bot()


if __name__ == '__main__':
    main()
