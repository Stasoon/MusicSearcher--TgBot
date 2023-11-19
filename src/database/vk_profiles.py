from peewee import IntegrityError, DoesNotExist
from .models import VkProfile, UserVkProfileRelation, User


### Профили ###

def create_or_update_profile(profile_id: int, name: str, username: str = None):
    try:
        # Попытка получить существующий профиль по profile_id
        profile = VkProfile.get(VkProfile.id == profile_id)

        # Если профиль существует, обновляем имя и юзернейм
        profile.name = name
        profile.username = username
        profile.save()
    except DoesNotExist:
        # Если профиля с таким profile_id нет, создаем новый
        profile = VkProfile.create(id=profile_id, name=name, username=username)

    return profile


def get_profile(profile_id: int) -> VkProfile | None:
    return VkProfile.get_or_none(VkProfile.id == profile_id)


### Сохранение профилей у юзеров ###

def save_vk_profile_for_user(user_telegram_id, vk_profile) -> bool:
    try:
        # Пытаемся создать новую запись в таблице UserVkProfileRelation
        user = User.get(User.telegram_id == user_telegram_id)
        UserVkProfileRelation.get_or_create(user=user, vk_profile=vk_profile)
        return True
    except IntegrityError:
        return False


def remove_vk_profile_from_user_saves(user_telegram_id: int, vk_profile: VkProfile) -> bool:
    try:
        # Удаляем отношение
        relation = (
            UserVkProfileRelation
            .select()
            .where(UserVkProfileRelation.vk_profile == vk_profile)
            .join(User)
            .where(User.telegram_id == user_telegram_id)
            .get()
        )
        relation.delete_instance()

        # Если больше нет ссылок на профиль, удаляем его из БД
        remaining_relations = UserVkProfileRelation.select().where(
            UserVkProfileRelation.vk_profile == vk_profile
        ).count()
        if not remaining_relations: vk_profile.delete()

        return True
    except DoesNotExist:
        return False


def get_vk_profiles_for_user(user_telegram_id: int):
    try:
        vk_profiles = VkProfile.select().join(UserVkProfileRelation).join(User).where(
            User.telegram_id == user_telegram_id)
        return list(vk_profiles)
    except DoesNotExist:
        # Обработка случая, когда пользователь не имеет связанных профилей
        return []
