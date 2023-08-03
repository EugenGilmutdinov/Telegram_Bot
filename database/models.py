from peewee import SqliteDatabase, Model, PrimaryKeyField, CharField, IntegerField, ForeignKeyField, DateTimeField, \
    FloatField
from config_data.config import BASE_DIR


database_path = BASE_DIR / 'database' / 'history.db'
db = SqliteDatabase(f'{database_path}')


class BaseModel(Model):
    """
    Базовый класс, описывающий пользователя

    Attributes:
        id (int): уникальный идентификатор

    """

    id = PrimaryKeyField(column_name='Id', null=False)

    class Meta:
        database = db


class User(BaseModel):
    """
    Класс Пользователь. Родитель: BaseModel

    Attributes:
        id (int): уникальный идентификатор
        name (str): имя пользователя
        telegram_id (int): идентификатор пользователя телеграм

    """
    id = PrimaryKeyField(column_name='UserId', null=False)
    name = CharField(column_name='Name')
    telegram_id = IntegerField(column_name='TelegramId')

    class Meta:
        table_name = 'User'


class Command(BaseModel):
    """
    Класс Команда. Родитель: BaseModel

    Attributes:
        name (str): имя пользователя, ссылающее на таблицу User
        command (str): выбранная пользователем команда
        send_date (str): дата и время выбранной команды

    """
    name = ForeignKeyField(User, to_field='name', related_name='commands', column_name='Name')
    command = CharField(column_name='Command')
    send_date = DateTimeField(column_name='SendDate')

    class Meta:
        table_name = 'Command'


class Hotel(BaseModel):
    """
    Класс Отель. Родитель: BaseModel

    Attributes:
        command_id (int): идентификатор команды, ссылающий на таблицу Command
        name (str): имя пользователя
        hotel_name (str): название отеля
        address (str): адрес отеля
        distance (str): дистанция от центра до отеля
        price (str): цена отеля
        rating (float): рейтинг отеля
        stars (float): звёздный рейтинг отеля
        outline_stars (int): недостающее кол-во звёзд до 5

    """
    command_id = ForeignKeyField(Command, backref='hotels', column_name='CommandId')
    name = CharField(column_name='Name')
    hotel_name = CharField(column_name='HotelName')
    address = CharField(column_name='Address')
    distance = CharField(column_name='Distance')
    price = CharField(column_name='Price')
    rating = FloatField(column_name='Rating')
    stars = FloatField(null=True, column_name='Stars+')
    outline_stars = IntegerField(null=True, column_name='Stars-')

    class Meta:
        table_name = 'Hotel'


tables = [User, Command, Hotel]
if not all(i.table_exists() for i in tables):
    db.create_tables([User, Command, Hotel])
