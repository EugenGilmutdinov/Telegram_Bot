from database.models import *
from loguru import logger
from typing import AnyStr, Dict, Any
import time


def add_user_to_db(message: Any) -> None:
    '''
    Функция для добавления пользователя в базу данных

    :param message: Api message
    :return: None
    '''

    telegram_id = message.from_user.id
    user_name = message.from_user.username
    with db:
        User.get_or_create(name=user_name, telegram_id=telegram_id)


def add_command_to_db(message=None, call=None) -> None:
    '''
    Функция для добавления команды выбранной пользователем в базу данных

    :param message: Api message
    :param call: Api call
    :return: None
    '''

    tconv = lambda x: time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(x))  # Конвертация даты в читабельный вид
    if message:
        name = message.from_user.username
        command = message.text
        date_and_time = tconv(message.date)
    else:
        name = call.from_user.username
        command = call.data
        date_and_time = tconv(call.message.date)
    with db:
        user = User.get_or_none(User.name == name)
        if user:
            Command.create(name=user, command=command, send_date=date_and_time)
        else:
            logger.error(f"Пользователь: {name} отсутствует в таблице User")
            if message:
                add_user_to_db(message)
            else:
                add_user_to_db(call)
            user = User.get(User.name == name)
            Command.create(name=user, command=command, send_date=date_and_time)


def add_hotel_to_db(message: Any, hotel: Dict, data: Dict) -> None:
    '''
    Функция для добавления информации об отеле в базу данных

    :param message: Api message
    :param hotel: dict - словарь с отелем
    :param data: словарь хранения данных о выборе пользователя
    :return: None
    '''

    user_name = message.from_user.username
    hotel_name = hotel['name']
    address = f"{hotel['streetAddress']} {hotel['extendedAddress']}"
    distance = str(hotel['distance']).replace('.', ',')
    distance = f"{distance} км"
    price = ''
    if len(data['currency']) == 2:
        price = f"{hotel['price']} {data['currency'][1]}"
    else:
        price = f"{hotel['price']} {data['currency']}"
    rating = hotel['rating']
    outline_stars = 5 - int(hotel['starRating'])
    with db:
        command = Command.select().where(Command.name == user_name).limit(1).order_by(Command.id.desc()).get()
        Hotel.create(command_id=command, name=user_name, hotel_name=hotel_name,
                     address=address, distance=distance, price=price, rating=rating,
                     stars=hotel['starRating'], outline_stars=outline_stars)


# def select_command_date(user):
#     cursor = db.cursor()
#     with db:
#         cursor.execute(f"SELECT command, send_date FROM Command WHERE user_name = '{user}' ORDER BY send_date DESC "
#                        f"LIMIT 1")
#         results = cursor.fetchall()
#         command = results[0][0]
#         date = results[0][1]
#         print(results)
#         return command, date


def select_command_date(user_name: AnyStr) -> tuple:
    '''
    Функция выбора подходящей команды и даты из базы данных

    :param user_name: AnyStr - имя пользователя
    :return: tuple - кортеж, включающий команду и дату
    '''
    with db:
        query = Command.select(Command.command, Command.send_date).where(Command.name == user_name).limit(1).order_by(
            Command.id.desc()).get()
        command, date = query.command, query.send_date
        return command, date


def select_hotels(user_name: AnyStr) -> Any:
    '''
    Функция выбора последних отелей из базы данных для данного пользователя

    :param user_name: AnyStr - имя пользователя
    :return: Any
    '''
    with db:
        last_command_id = Command.select(Command.id).where(Command.name == user_name).limit(1).order_by(
            Command.id.desc()).get()
        hotels = Hotel.select().where(Hotel.command_id == last_command_id)
        return hotels
