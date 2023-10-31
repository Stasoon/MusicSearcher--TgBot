from peewee import Model, SqliteDatabase, IntegerField, DateTimeField, CharField, TextField, BooleanField


db = SqliteDatabase('database.db')


class _BaseModel(Model):
    class Meta:
        database = db


class User(_BaseModel):
    telegram_id = IntegerField(unique=True, null=False)
    name = CharField(default='Пользователь')
    username = CharField(null=True, default='Пользователь')
    lang_code = CharField(max_length=2, null=True, default=None)
    referral_link = CharField(null=True)
    registration_timestamp = DateTimeField()


class SongHash(_BaseModel):
    song_id = IntegerField(unique=True)
    owner_id = IntegerField()
    file_id = CharField(max_length=150, unique=True)


class Advertisement(_BaseModel):
    text = TextField()
    showed_count = IntegerField(default=0)
    is_active = BooleanField(default=True)


class ReferralLink(_BaseModel):
    name = CharField(unique=True)
    user_count = IntegerField(default=0)
    passed_op_count = IntegerField(default=0)


class Admin(_BaseModel):
    telegram_id = IntegerField(unique=True, null=False)
    name = CharField()


class Channel(_BaseModel):
    channel_id = IntegerField()
    title = CharField()
    url = CharField()


class PopularSongsCatalog(_BaseModel):
    owner_id = IntegerField()
    song_id = IntegerField()
    title = CharField()
    artist = CharField()
    duration = IntegerField()


class NewSongsCatalog(_BaseModel):
    owner_id = IntegerField()
    song_id = IntegerField()
    title = CharField()
    artist = CharField()
    duration = IntegerField()


def register_models() -> None:
    for model in _BaseModel.__subclasses__():
        model.create_table()
