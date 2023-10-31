from peewee import Model, SqliteDatabase, IntegerField, DateTimeField, CharField


db = SqliteDatabase('database.db')


class _BaseModel(Model):
    class Meta:
        database = db


class User(_BaseModel):
    name = CharField(default='Пользователь')
    telegram_id = IntegerField(unique=True, null=False)
    registration_timestamp = DateTimeField()
    referral_link = CharField(null=True)

    class Meta:
        db_table = 'users'


class ReferralLink(_BaseModel):
    class Meta:
        db_table = 'referral_links'

    name = CharField(unique=True)
    user_count = IntegerField(default=0)
    passed_op_count = IntegerField(default=0)


def register_models() -> None:
    for model in _BaseModel.__subclasses__():
        model.create_table()
