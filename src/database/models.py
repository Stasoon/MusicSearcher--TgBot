from peewee import (
    Model, PostgresqlDatabase, AutoField,
    SmallIntegerField, BigIntegerField, IntegerField,
    DateTimeField, CharField, TextField, BooleanField,
    ForeignKeyField
)
from config import DatabaseConfig


db = PostgresqlDatabase(
    DatabaseConfig.NAME,
    user=DatabaseConfig.USER, password=DatabaseConfig.PASSWORD,
    host=DatabaseConfig.HOST, port=DatabaseConfig.PORT
)


class _BaseModel(Model):
    class Meta:
        database = db


class User(_BaseModel):
    """ Пользователь бота """
    class Meta:
        db_table = 'users'

    telegram_id = BigIntegerField(primary_key=True, unique=True, null=False)
    name = CharField(default='Пользователь')
    username = CharField(null=True, default='Пользователь')
    lang_code = CharField(max_length=2, null=True, default=None)
    referral_link = CharField(null=True)
    registration_timestamp = DateTimeField()


class Subscription(_BaseModel):
    """ Подписка на бота """
    class Meta:
        db_table = 'subscriptions'

    subscriber = ForeignKeyField(User)


class AdShowCounter(_BaseModel):
    """ Счётчик показов реклам для пользователя """
    user_telegram_id = BigIntegerField()
    count = SmallIntegerField(default=0)


class Advertisement(_BaseModel):
    """ Реклама для показа пользователю """
    class Meta:
        db_table = 'advertisements'

    id = AutoField(primary_key=True)
    text = TextField()
    markup_json = TextField(null=True)
    showed_count = IntegerField(default=0)
    is_active = BooleanField(default=True)


class ReferralLink(_BaseModel):
    """ Реферальная ссылка """
    class Meta:
        db_table = 'referral_links'

    name = CharField(unique=True)
    user_count = IntegerField(default=0)
    passed_op_count = IntegerField(default=0)


class JoinRequestChannel(_BaseModel):
    """ Канал, заявки на вступление в который должен обрабатывать бот """
    class Meta:
        db_table = 'join_request_channels'

    channel_id = BigIntegerField(primary_key=True)
    channel_title = CharField()
    invite_link = CharField()
    welcome_text = TextField()
    approved_requests_count = IntegerField(default=0)


class Admin(_BaseModel):
    """ Администратор бота """
    class Meta:
        db_table = 'admins'

    telegram_id = BigIntegerField(unique=True, null=False)
    name = CharField()


class SubscriptionChannels(_BaseModel):
    """" Канал для обязательной подписки """
    class Meta:
        db_table = 'subscription_channels'

    channel_id = BigIntegerField()
    title = CharField()
    url = CharField()


class SongHash(_BaseModel):
    """ Кэш песни, которая была отправлена пользователю """
    class Meta:
        db_table = 'songs_hashes'

    song_id = BigIntegerField()
    owner_id = BigIntegerField()
    file_id = CharField(max_length=150, unique=True)


class PopularSongsCatalog(_BaseModel):
    class Meta:
        db_table = 'popular_songs_catalog'

    owner_id = BigIntegerField()
    song_id = BigIntegerField()
    title = CharField()
    artist = CharField()
    duration = SmallIntegerField()


class NewSongsCatalog(_BaseModel):
    class Meta:
        db_table = 'new_songs_catalog'

    owner_id = BigIntegerField()
    song_id = BigIntegerField()
    title = CharField()
    artist = CharField()
    duration = SmallIntegerField()


class VkProfile(_BaseModel):
    """ Профиль человека/группы ВКонтакте """
    id = BigIntegerField(primary_key=True, unique=True)
    name = CharField(max_length=300)


class UserVkProfileRelation(_BaseModel):
    """ Отношение пользователь бота - сохранённый им профиль ВКонтакте """
    user = ForeignKeyField(User)
    vk_profile = ForeignKeyField(VkProfile)


def register_models() -> None:
    for model in _BaseModel.__subclasses__():
        model.create_table()
