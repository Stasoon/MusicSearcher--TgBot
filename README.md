1) Создание локализаций (PyBabel):
- Добавить локализацию:
pybabel init -i locales/messages.pot -d locales -D messages -l ru
- Извлечь тексты из скриптов:
pybabel extract --input-dirs=src/ -o locales/messages.pot
- Обновить файлы с локализациями:
pybabel update -d locales -D messages -i locales/messages.pot 
- Сохранить локаизации:
pybabel compile -d locales -D messages


2) Парсинг с динамических страниц ВК новых и популярных песен на Linux (selenium):
- python -m playwright install chromium
- python -m playwright install-deps
- sudo apt install ffmpeg 