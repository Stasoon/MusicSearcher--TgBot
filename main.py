from src.start_bot import start_bot
from src.utils import setup_logger

# Получение нового токена
# from src.utils.vkpymusic.create_acc import authorize_and_get_token
# authorize_and_get_token(login='+79268420794', password='Stas123456/')


def main():
    setup_logger()
    start_bot()


if __name__ == '__main__':
    main()
