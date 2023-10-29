import random

from .models import Advertisement


# Create
def create_ad(text: str):
    Advertisement.create(text=text)


# Read
def get_active_ads():
    return Advertisement.select().where(Advertisement.is_active == True)


def get_random_ad() -> str | None:
    # Получить все активные рекламные записи
    active_ads = Advertisement.select().where(Advertisement.is_active == True)

    if not active_ads:
        return None

    # Получаем случайную рекламу
    random_ad = random.choice(active_ads)

    # Увеличиваем счетчик показов
    random_ad.showed_count += 1
    random_ad.save()

    return random_ad.text


# Delete
def delete_ad(advertisement_id: int) -> bool:
    try:
        ad = Advertisement.get(Advertisement.id == advertisement_id)
        ad.delete_instance()
        return True  # Возвращаем True, если удаление прошло успешно
    except Advertisement.DoesNotExist:
        return False  # Возвращаем False, если реклама с указанным идентификатором не найдена
