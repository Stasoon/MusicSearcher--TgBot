1) PyBabel:
- Обновить
pybabel extract --input-dirs=src/ -o locales/messages.pot
- Добавить язык:
pybabel init -i locales/messages.pot -d locales -D messages -l ru
- Сохранить изменения
pybabel compile -d locales -D messages