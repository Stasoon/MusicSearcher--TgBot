from .models import User, Subscription


def add_subscribed_user(telegram_id: int) -> Subscription | None:
    """ Создать подписку """
    user = User.get_or_none(User.telegram_id == telegram_id)
    if not user:
        return None

    subscription, _ = Subscription.get_or_create(subscriber=user)
    return subscription


def has_subscription(user_id) -> bool:
    """ Проверка, есть ли подписка у пользователя """
    return Subscription.select().where(Subscription.subscriber == user_id).exists()


def get_users_with_subscription() -> list[User]:
    """ Получение списка пользователей с подпиской """
    return User.select().join(Subscription).distinct()
