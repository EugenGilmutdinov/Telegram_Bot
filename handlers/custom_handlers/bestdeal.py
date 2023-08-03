from loader import bot
from loguru import logger
from states.info_for_commands import UserInfoState
from telebot.types import Message
from telebot.types import ReplyKeyboardRemove
from keyboards.inline import site_and_geo, num_hotels, commands
from keyboards.reply import total_photos
from database import *
from time import sleep

from rapid_api import api
from handlers.custom_handlers.functions import show_result


@bot.message_handler(state=UserInfoState.price_range)
def get_price_range(message: Message) -> None:
    '''
    Хэндлер состояния "price_range", возникающий при условии, что выбрана команда "bestdeal"
    Предназначен для выбора диапазона цен отелей
    Присваивает состояние "distance_range"

    :param message: сообщение пользователя
    :return: None
    '''
    try:
        price = message.text.split(' ')
        price = list(map(lambda x: int(x) if '.' not in x else float(x), price))
        if len(price) == 2:
            with bot.retrieve_data(message.from_user.id) as data:
                data['price_range'] = price

            bot.send_message(message.chat.id, 'Далее введите диапазон расстояния через пробел (км.),\n'
                                              'на котором находится отель от центра.\n'
                                              'Пример : 0.1 20')

            bot.set_state(message.from_user.id, UserInfoState.distance_range)
        else:
            logger.info(f"Диапазон цен: {message.text} некорректный")
            bot.reply_to(message, 'Ошибка ввода!\nВведите пожалуйста 2 числа через пробел,\n'
                                  'пример: 1000 30000')
    except ValueError:
        logger.info(f"Неверное значение диапазона цен: {message.text}")
        bot.reply_to(message, 'Ошибка ввода!\nВведите пожалуйста числа через пробел,\n'
                              'пример: 1000 30000')


@bot.message_handler(state=UserInfoState.distance_range)
def get_distance_range(message: Message) -> None:
    '''
    Хэндлер состояния "distance_range", возникающий при условии, что выбрана команда "bestdeal"
    Предназначен для выбора диапазона отдаленности от центра
    Запрашивает информацию для вывода о количестве отелей
    Присваивает состояние "num_hotels"

    :param message: сообщение пользователя
    :return: None
    '''
    try:
        distance = message.text.split(' ')
        if len(distance) == 2:
            distance = list(map(lambda x: int(x) if '.' not in x else float(x), distance))
            distance_mile_km = distance.copy()
            if distance_mile_km[0] != 0:
                distance_mile_km[0] = round(distance_mile_km[0] / 1.609, 1)
            if distance_mile_km[1] != 0:
                distance_mile_km[1] = round(distance_mile_km[1] / 1.609, 1)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['distance_range'] = distance_mile_km
                data['distance_mile'] = distance
            bot.send_message(message.chat.id,
                             'Выберете количество отелей, которые необходимо вывести (не более 10)',
                             reply_markup=num_hotels.total_hotels())
            bot.set_state(message.chat.id, UserInfoState.num_hotels)
        else:
            logger.info(f"Диапазон расстояния: {message.text} некорректный")
            bot.reply_to(message, 'Ошибка ввода!\nВведите пожалуйста 2 числа через пробел,\n'
                                  'пример: 0.1 20')
    except ValueError:
        logger.info(f"Неверное значение диапазона расстояния: {message.text}")
        bot.reply_to(message, 'Ошибка ввода!\nВведите диапазон расстояния через пробел (км.),\n'
                              'на котором находится отель от центра.\n'
                              'Пример : 0.1 20')


@bot.message_handler(state=UserInfoState.display_result_bestdeal)
def get_need_photo(message: Message) -> None:
    '''
    Хэндлер, выводящий итоговую информацию о найденных отелях
    Принимает сообщение о выборе пользователем в выводе фотографий
    Присваивает начальное состояние повторного выбора команд "command"

    :param message: сообщение пользователя
    :return: None
    '''
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['need_photo'] = message.text

    if data['need_photo'] == "Да":
        bot.send_message(message.chat.id,
                         "Выберете количество фотографий, которые необходимо вывести (не более 10)",
                         reply_markup=total_photos.total_hotels())

        bot.set_state(message.from_user.id, UserInfoState.get_photos_bestdeal, message.chat.id)
    if data['need_photo'] == "Нет":
        wait = bot.send_message(message.chat.id, "Запрос отелей. Подождите, длительная операция... ⌛",
                                reply_markup=ReplyKeyboardRemove())
        response = api.request_to_hotels(data)
        hotels_dict = api.checking_response(response)
        if not hotels_dict:
            bot.delete_message(message.chat.id, wait.message_id)
            info = f'В вашем диапазоне цен (от {data["price_range"][0]} ' \
                   f'до {data["price_range"][1]} рублей) отелей не найдено.'
            logger.info(info)
            bot.send_message(message.chat.id, f'{info}\nПопробуйте изменить критерии')
            bot.send_message(message.chat.id, 'Введите диапазон цен через пробел (RUB),\n'
                                              'пример : 1000 30000')
            bot.set_state(message.from_user.id, UserInfoState.price_range, message.chat.id)
        else:
            hotels = show_result.show_hotels_bestdeal(hotels_dict, data['distance_range'])
            bot.delete_message(message.chat.id, wait.message_id)
            if hotels:
                currency = 0
                if "BYN" in data['currency']:
                    currency = api.request_to_api_currency()
                for i, hotel in enumerate(hotels):
                    i += 1
                    info = show_result.show_hotel_info(hotel, data, currency)
                    web_site_keyboard = site_and_geo.site_location_markup(hotel['id'], hotel['coordinate'])
                    bot.send_message(message.chat.id, f"<strong>{i}.</strong>\n{info}",
                                     reply_markup=web_site_keyboard, parse_mode='html')
                    db_requests.add_hotel_to_db(message, hotel, data)
                sleep(3)

                bot.send_message(message.from_user.id, 'Выберете одну из команд:', reply_markup=commands.menu_markup())
                bot.set_state(message.from_user.id, UserInfoState.command)
            else:
                info = f'В вашем диапазоне расстояния (от {data["distance_mile"][0]} ' \
                       f'до {data["distance_mile"][1]} км) отелей не найдено.'
                logger.info(info)
                bot.send_message(message.chat.id, f'{info}\nПопробуйте изменить критерии')
                bot.send_message(message.chat.id, 'Введите диапазон расстояния через пробел (км.),\n'
                                                  'на котором находится отель от центра.\n'
                                                  'Пример : 0.1 20')

                bot.set_state(message.from_user.id, UserInfoState.distance_range, message.chat.id)


@bot.message_handler(state=UserInfoState.get_photos_bestdeal)
def show_photos(message: Message) -> None:
    '''
    Хэндлер, возникающий при выборе вывода фотографий
    Выводит итоговую информацию о найденных отелях с фотографиями
    Присваивает начальное состояние повторного выбора команд "command"

    :param message: сообщение пользователя
    :return: None
    '''
    wait = bot.send_message(message.chat.id, "Запрос отелей. Подождите, длительная операция... ⌛",
                            reply_markup=ReplyKeyboardRemove())
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['num_hotel_photos'] = int(message.text)
    response = api.request_to_hotels(data)
    hotels_dict = api.checking_response(response)
    if not hotels_dict:
        bot.delete_message(message.chat.id, wait.message_id)
        info = f'В вашем диапазоне цен (от {data["price_range"][0]} ' \
               f'до {data["price_range"][1]} рублей) отелей не найдено.'
        logger.info(info)
        bot.send_message(message.chat.id, f'{info}\nПопробуйте изменить критерии')
        bot.send_message(message.chat.id, 'Введите диапазон цен через пробел (RUB),\n'
                                          'пример: 1000 30000')
        bot.set_state(message.from_user.id, UserInfoState.price_range, message.chat.id)
    else:
        hotels = show_result.show_hotels_bestdeal(hotels_dict, data['distance_range'])
        bot.delete_message(message.chat.id, wait.message_id)
        if hotels:
            currency = 0
            if "BYN" in data['currency']:
                currency = api.request_to_api_currency()
            for i, hotel in enumerate(hotels):
                i += 1
                info = show_result.show_hotel_info(hotel, data, currency)
                response_photos = api.request_to_photos(hotel['id'])
                hotel_photos = show_result.photos(response_photos, data["num_hotel_photos"], info, i)
                web_site_keyboard = site_and_geo.site_location_markup(hotel['id'], hotel['coordinate'])
                bot.send_media_group(message.from_user.id, hotel_photos)
                bot.send_message(message.chat.id, f"Дополнительная информация:",
                                 reply_markup=web_site_keyboard, parse_mode='html')
                db_requests.add_hotel_to_db(message, hotel, data)
            sleep(3)

            bot.send_message(message.from_user.id, 'Выберете одну из команд:', reply_markup=commands.menu_markup())
            bot.set_state(message.from_user.id, UserInfoState.command)
        else:
            info = f'В вашем диапазоне расстояния (от {data["distance_mile"][0]} ' \
                   f'до {data["distance_mile"][1]} км) отелей не найдено.'
            logger.info(info)
            bot.send_message(message.chat.id, f'{info}\nПопробуйте изменить критерии')
            bot.send_message(message.chat.id, 'Введите диапазон расстояния через пробел (км.),\n'
                                              'на котором находится отель от центра.\n'
                                              'Пример : 0.1 20')

            bot.set_state(message.from_user.id, UserInfoState.distance_range, message.chat.id)
