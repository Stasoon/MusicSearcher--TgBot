import random
import json

from .models import Advertisement, AdShowCounter


# Create
def create_ad(text: str, markup_json: str | dict = None) -> None:
    markup_data = str(markup_json) if markup_json else None
    Advertisement.create(text=text, markup_json=markup_data)


def increase_counter_and_get_value(user_id) -> int:
    counter, created = AdShowCounter.get_or_create(user_telegram_id=user_id)
    if not created:
        counter.count += 1
        counter.save()
    return counter.count


def reset_counter(user_id) -> None:
    counter, created = AdShowCounter.get_or_create(user_telegram_id=user_id)
    if not created:
        counter.count = 0
        counter.save()


# Read
def get_active_ads() -> list[Advertisement]:
    return Advertisement.select().where(Advertisement.is_active == True)


def get_random_ad() -> Advertisement | None:
    # Получить все активные рекламные записи
    active_ads = Advertisement.select().where(Advertisement.is_active == True)

    if not active_ads:
        return None

    # Получаем случайную рекламу
    random_ad: Advertisement = random.choice(active_ads)

    # Увеличиваем счетчик показов
    random_ad.showed_count += 1
    random_ad.save()

    # Делаем markup в полученном объекте словарём
    if random_ad.markup_json:
        random_ad.markup_json = json.loads(random_ad.markup_json)
    return random_ad


# Delete
def delete_ad(advertisement_id: int) -> bool:
    try:
        ad = Advertisement.get(Advertisement.id == advertisement_id)
        ad.delete_instance()
        return True  # Возвращаем True, если удаление прошло успешно
    except Advertisement.DoesNotExist:
        return False  # Возвращаем False, если реклама с указанным идентификатором не найдена
