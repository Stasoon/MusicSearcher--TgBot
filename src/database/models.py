from peewee import (
    Model, PostgresqlDatabase, AutoField,
    SmallIntegerField, BigIntegerField, IntegerField,
    DateTimeField, CharField, TextField, BooleanField
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
    class Meta:
        db_table = 'users'

    telegram_id = BigIntegerField(primary_key=True, unique=True, null=False)
    name = CharField(default='Пользователь')
    username = CharField(null=True, default='Пользователь')
    lang_code = CharField(max_length=2, null=True, default=None)
    referral_link = CharField(null=True)
    registration_timestamp = DateTimeField()


class AdShowCounter(_BaseModel):
    user_telegram_id = BigIntegerField()
    count = SmallIntegerField(default=0)


class Advertisement(_BaseModel):
    class Meta:
        db_table = 'advertisements'

    id = AutoField(primary_key=True)
    text = TextField()
    markup_json = TextField(null=True)
    showed_count = IntegerField(default=0)
    is_active = BooleanField(default=True)


class SongHash(_BaseModel):
    class Meta:
        db_table = 'songs_hashes'

    song_id = BigIntegerField()
    owner_id = BigIntegerField()
    file_id = CharField(max_length=150, unique=True)


class ReferralLink(_BaseModel):
    class Meta:
        db_table = 'referral_links'

    name = CharField(unique=True)
    user_count = IntegerField(default=0)
    passed_op_count = IntegerField(default=0)


class Admin(_BaseModel):
    class Meta:
        db_table = 'admins'

    telegram_id = BigIntegerField(unique=True, null=False)
    name = CharField()


class Channel(_BaseModel):
    class Meta:
        db_table = 'channels'

    channel_id = BigIntegerField()
    title = CharField()
    url = CharField()


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


def register_models() -> None:
    for model in _BaseModel.__subclasses__():
        model.create_table()
