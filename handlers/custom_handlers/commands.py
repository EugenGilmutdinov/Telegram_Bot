from loader import bot
import json
from states.info_for_commands import UserInfoState
from telebot.types import Message
from loguru import logger
from datetime import date

from keyboards.inline.filters_calendar import calendar_factory, calendar_zoom, first_date_check, full_date_check
from keyboards.inline.calendar_keyboard import generate_calendar_days, generate_calendar_months, chosen_calendar_day
from database import *
from telebot import types
from telebot.types import ReplyKeyboardRemove
from keyboards.inline import currency_keyboard, num_hotels, site_and_geo, commands
from keyboards.reply import yes_no, total_photos
import locale
from time import sleep

from rapid_api import api
from handlers.custom_handlers.functions import show_result


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def lowprice(message: Message) -> None:
    '''
    Хэндлер команд 'lowprice', 'highprice', 'bestdeal'
    Попадаем в него при выборе одной из команд через знак "/"
    Запрашивает параметры у пользователя, затем присваивает состояние "city"

    :param message: сообщение пользователя
    :return: None
    '''
    db_requests.add_command_to_db(message=message)
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text
    bot.send_message(message.chat.id, f"Введите город поиска отелей:")


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    '''
    Хэндлер состояния "city"
    Принимает сообщение от пользователя с названием города поиска отелей
    Запрашивает выбор города с помощью инлайн клавиатуры, затем присваивает состояние "checkIn"

    :param message: сообщение пользователя
    :return: None
    '''
    city = message.text
    cities_keyboard = api.request_to_city(city)
    if cities_keyboard:
        bot.send_message(message.chat.id, 'Уточните, пожалуйста:', reply_markup=cities_keyboard)
        bot.set_state(message.from_user.id, UserInfoState.checkIn, message.chat.id)
    else:
        logger.error(f"Город: {city} не найден")
        bot.send_message(message.chat.id, f"Город: {city} не найден")
        bot.send_message(message.chat.id, f"Введите пожалуйста другой город:")


@bot.callback_query_handler(state=UserInfoState.checkIn, func=lambda c: c.data.isdigit() and len(c.data) > 2)
def callback(call: types.CallbackQuery) -> None:
    '''
    Коллбэк квэри хэндлер состояния "checkIn"
    Принимает название города, затем запрашивает информацию у пользователя о дате въезда,
    через инлайн клавиатуру. Присваивает состояние "checkOut"

    :param call: данные кнопки инлайн клавиатуры в запросе обратного вызова
    :return: None
    '''
    bot.answer_callback_query(call.id)

    with bot.retrieve_data(call.from_user.id) as data:
        data['city'] = call.data

    now = date.today()
    bot.send_message(call.from_user.id, 'Далее выберете дату въезда:',
                     reply_markup=generate_calendar_days(year=now.year, month=now.month))

    bot.set_state(call.from_user.id, UserInfoState.checkOut)


@bot.callback_query_handler(state=UserInfoState.checkOut, func=None, calendar_config=calendar_factory.filter())
def calendar_action_handler(call: types.CallbackQuery) -> None:
    '''
    Коллбэк квэри хэндлер с указанием действия пользователя
    Принимает выбранную дату пользователем и изменяет вывод инлайн клавиатуры с календарем

    :param call: данные кнопки инлайн клавиатуры в запросе обратного вызова
    :return: None
    '''
    callback_data: dict = calendar_factory.parse(callback_data=call.data)
    year, month = int(callback_data['year']), int(callback_data['month'])
    if callback_data.get('day'):
        day = callback_data['day']
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                      reply_markup=chosen_calendar_day(ch_year=year, ch_month=month, ch_day=day))
    else:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                      reply_markup=generate_calendar_days(year=year, month=month))


@bot.callback_query_handler(state=UserInfoState.checkOut, func=None, calendar_zoom_config=calendar_zoom.filter())
def calendar_zoom_out_handler(call: types.CallbackQuery) -> None:
    '''
    Коллбэк квэри хэндлер, возникающий при нажатии инлайн кнопки "Отдалить"
    Изменяет инлайн клавиатуру для вывода месяцев

    :param call: данные кнопки инлайн клавиатуры в запросе обратного вызова
    :return: None
    '''
    callback_data: dict = calendar_zoom.parse(callback_data=call.data)
    year = int(callback_data.get('year'))

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                  reply_markup=generate_calendar_months(year=year))

    bot.set_state(call.from_user.id, UserInfoState.checkOut)


@bot.callback_query_handler(state=UserInfoState.checkOut, func=lambda call: first_date_check(call.data))
def callback_checkout_handler(call: types.CallbackQuery) -> None:
    '''
    Коллбэк квэри хэндлер, принимающий дату въезда
    Изменяет инлайн клавиатуру для выбора пользователем даты выезда
    Присваивает состояние "checkIn_Out"

    :param call: данные кнопки инлайн клавиатуры в запросе обратного вызова
    :return: None
    '''
    locale.setlocale(
        category=locale.LC_ALL,
        locale="Russian"
    )
    bot.answer_callback_query(call.id)
    year, month, day = list(map(lambda x: int(x), call.data.split('-')))
    bot.edit_message_text('Теперь выберете пожалуйста дату выезда:', call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=chosen_calendar_day(ch_year=year, ch_month=month, ch_day=day))
    bot.set_state(call.from_user.id, UserInfoState.checkIn_Out)


@bot.callback_query_handler(state=UserInfoState.checkIn_Out, func=lambda call: full_date_check(call.data))
def callback_checkin_out_handler(call: types.CallbackQuery) -> None:
    '''
    Коллбэк квэри хэндлер, принимающий дату выезда
    Отправляет сообщение с информацией о дате въезда и выезда, выбранной пользователем
    Присваивает состояние "num_hotels"

    :param call: данные кнопки инлайн клавиатуры в запросе обратного вызова
    :return: None
    '''
    bot.answer_callback_query(call.id)
    full_date = call.data.split(', ')
    checkIn = full_date[0]
    checkOut = full_date[1]
    with bot.retrieve_data(call.from_user.id) as data:
        data['checkIn'] = checkIn
        data['checkOut'] = checkOut
    year_1, month_1, day_1 = list(map(lambda x: int(x), checkIn.split('-')))
    year_2, month_2, day_2 = list(map(lambda x: int(x), checkOut.split('-')))
    first_date = date(year_1, month_1, day_1)
    second_date = date(year_2, month_2, day_2)
    first_day_month = first_date.strftime('%d %B').lower()
    second_day_month = second_date.strftime('%d %B').lower()
    num_days = second_date - first_date
    num_days = str(num_days).split()[0]
    bot.send_message(call.from_user.id, f"<strong>Дата въезда\выезда:</strong> c {first_day_month} "
                                        f"по {second_day_month} ({num_days} дней)", parse_mode='html')
    with bot.retrieve_data(call.from_user.id) as data:
        data['num_days'] = num_days

    if data['command'] == '/bestdeal':
        bot.send_message(call.from_user.id, 'Введите диапазон цен через пробел (RUB),\n'
                                            'пример: 1000 30000')
        bot.set_state(call.from_user.id, UserInfoState.price_range)
    else:
        bot.send_message(call.from_user.id,
                         'Выберете количество отелей, которые необходимо вывести (не более 10)',
                         reply_markup=num_hotels.total_hotels())
        bot.set_state(call.from_user.id, UserInfoState.num_hotels)


@bot.callback_query_handler(state=UserInfoState.num_hotels, func=lambda c: c.data.isdigit() and len(c.data) <= 2)
def num_hotels_callback(call: types.CallbackQuery) -> None:
    '''
    Коллбэк квэри хэндлер, принимающий количество отелей, выбранное пользователем
    Запрашивает информацию о валюте стоимости отелей
    Присваивает состояние "currency"

    :param call: данные кнопки инлайн клавиатуры в запросе обратного вызова
    :return: None
    '''
    bot.answer_callback_query(call.id)

    bot.send_message(call.from_user.id, f'Выберите валюту стоимости отелей:',
                     reply_markup=currency_keyboard.currency_markup())

    with bot.retrieve_data(call.from_user.id) as data:
        data['num_hotels'] = call.data
    bot.set_state(call.from_user.id, UserInfoState.currency)


@bot.callback_query_handler(state=UserInfoState.currency,
                            func=lambda c: c.data == "USD" or c.data == "RUB" or c.data == "BYN")
def currency_callback(call: types.CallbackQuery) -> None:
    '''
    Коллбэк квэри хэндлер, принимающий валюту стоимости отелей, выбранную пользователем
    Запрашивает информацию о нуждаемости в выводе фотографий для каждого отеля
    Если команда "bestdeal" присваивает состояние "display_result_bestdeal", иначе "display_result"

    :param call: данные кнопки инлайн клавиатуры в запросе обратного вызова
    :return: None
    '''
    bot.send_message(call.from_user.id, f'Отлично! Выводить фотографии для каждого отеля?',
                     reply_markup=yes_no.photo_output())

    with bot.retrieve_data(call.from_user.id) as data:
        if call.data == "BYN":
            data['currency'] = ["RUB", call.data]
        else:
            data['currency'] = call.data

    if data['command'] == "/bestdeal":
        bot.set_state(call.from_user.id, UserInfoState.display_result_bestdeal)
    else:
        bot.set_state(call.from_user.id, UserInfoState.display_result)

    bot.answer_callback_query(call.id)


@bot.message_handler(state=UserInfoState.display_result)
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
        bot.set_state(message.from_user.id, UserInfoState.get_photos, message.chat.id)

    if data['need_photo'] == "Нет":
        wait = bot.send_message(message.chat.id, "Запрос отелей. Подождите, длительная операция... ⌛",
                                reply_markup=ReplyKeyboardRemove())
        response = api.request_to_hotels(data)
        res = json.loads(response.text)
        city = res['data']['body'].get('header')
        total_hotels = res['data']['body']['searchResults'].get('totalCount')
        if total_hotels == 0:
            logger.debug(f"В городе: {city} отелей не найдено")
            bot.send_message(message.chat.id, f"В городе: {city} отелей не найдено")

            bot.send_message(message.from_user.id, 'Выберете одну из команд:', reply_markup=commands.menu_markup())
            bot.set_state(message.from_user.id, UserInfoState.command)
        else:
            hotels = show_result.show_hotels(response)
            currency = 0
            if "BYN" in data['currency']:
                currency = api.request_to_api_currency()
            bot.delete_message(message.chat.id, wait.message_id)
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


@bot.message_handler(state=UserInfoState.get_photos)
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
    hotels = show_result.show_hotels(response)
    currency = 0
    if "BYN" in data['currency']:
        currency = api.request_to_api_currency()
    bot.delete_message(message.chat.id, wait.message_id)
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
