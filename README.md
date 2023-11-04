1) Создание локализаций (PyBabel):
- Добавить локализацию:
pybabel init -i locales/messages.pot -d locales -D messages -l ru
- Извлечь тексты из скриптов:
pybabel extract --input-dirs=src/ -o locales/messages.pot
- Обновить файлы с локализациями:
pybabel update -d locales -D messages -i locales/messages.pot 
- Сохранить локализации:
pybabel compile -d locales -D messages

2) Парсинг с динамических страниц ВК новых и популярных песен на Linux:
- python -m playwright install chromium
- python -m playwright install-deps
- sudo apt install ffmpeg 

3) Создать файл ".env" и в него добавить:
BOT_TOKEN=12345678:AbCDEF_gEodJGIfIeFDhjvUI
ADMIN_IDS=123456,789101112
VK_LOGIN=changeme
VK_PASSWORD=changeme

DB_USER=changeme
DB_PASSWORD=changeme
DB_NAME=changeme
DB_HOST=localhost
DB_PORT=5432

