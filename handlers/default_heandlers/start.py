from telebot import types
from telebot.types import Message
from states.info_for_commands import UserInfoState
from config_data.config import DEFAULT_COMMANDS, BASE_DIR
from loader import bot
from database import *
from handlers.custom_handlers.functions import write_information
from keyboards.inline import commands
import datetime
from time import sleep


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    '''
    Хэндлер команды 'start'
    Приветствует пользователя телеграм бота, дает информацию о предоставляемых командах
    Присваивает начальное состояние выбора команд "command"

    :param message: сообщение пользователя
    :return: None
    '''
    db_requests.add_user_to_db(message)
    dt = datetime.datetime.now()
    tm = dt.hour
    greeting_string = ""
    if 0 <= tm < 6:  # ночь
        greeting_string = f"Доброго времени суток"
    elif 6 <= tm < 12:  # утро
        greeting_string = f"Доброе утро"
    elif 12 <= tm < 18:  # день
        greeting_string = f"Добрый день"
    elif 18 <= tm < 24:  # вечер
        greeting_string = f"Добрый вечер"
    send_mess = f"{greeting_string}, <b>{message.from_user.username}</b>!\n" \
                f"Я помощник выбора отелей\nМоя задача найти тебе <b><u>лучшие отели</u></b>!"
    bot.send_message(message.from_user.id, send_mess, parse_mode='html')
    information = 'Мои возможности:\n' \
                  '▪ <strong>lowprice</strong> (топ самых дешёвых отелей в городе)\n' \
                  '▪ <strong>highprice</strong> (топ самых дорогих отелей в городе)\n' \
                  '▪ <strong>bestdeal</strong> (отели, наиболее подходящие по цене и расположению от центра)\n' \
                  '▪ <strong>history</strong> (история поиска отелей)\n' \
                  '▪ <strong>help</strong> (вывести справку)'
    bot.send_message(message.from_user.id, information, parse_mode='html')
    bot.send_message(message.from_user.id, 'Выберете одну из команд:', reply_markup=commands.menu_markup())
    bot.set_state(message.from_user.id, UserInfoState.command)


@bot.callback_query_handler(state=UserInfoState.command,
                            func=lambda call: call.data in ["/lowprice", "/highprice", "/bestdeal"])
def callback_command(call: types.CallbackQuery) -> None:
    '''
    Коллбэк квэри хэндлер состояния "command"
    Возникает при выборе команд "/lowprice", "/highprice", "/bestdeal"
    Запрашивает параметры у пользователя, затем присваивает состояние "city"

    :param call: данные кнопки инлайн клавиатуры в запросе обратного вызова
    :return: None
    '''
    bot.answer_callback_query(call.id)
    db_requests.add_command_to_db(call=call)
    bot.set_state(call.from_user.id, UserInfoState.city)
    with bot.retrieve_data(call.from_user.id) as data:
        data['command'] = call.data
    bot.send_message(call.from_user.id, f"Введите город поиска отелей:")


@bot.callback_query_handler(state=UserInfoState.command, func=lambda call: call.data == '/help')
def callback_help(call: types.CallbackQuery) -> None:
    '''
    Коллбэк квэри хэндлер состояния "command"
    Возникает при выборе команды "/help"
    Выводит вспомогательную информацию о предоставляемом выборе команд
    Присваивает начальное состояние выбора команд "command"

    :param call: данные кнопки инлайн клавиатуры в запросе обратного вызова
    :return: None
    '''
    bot.answer_callback_query(call.id)
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.send_message(call.from_user.id, '\n'.join(text))
    sleep(3)

    bot.send_message(call.from_user.id, 'Выберете одну из команд:', reply_markup=commands.menu_markup())
    bot.set_state(call.from_user.id, UserInfoState.command)


@bot.callback_query_handler(state=UserInfoState.command, func=lambda call: call.data == '/history')
def callback_history(call: types.CallbackQuery) -> None:
    '''
    Коллбэк квэри хэндлер состояния "command"
    Возникает при выборе команды "/history"
    Выводит информацию об уже показанных отелях, повторно выводя их на экран при помощи генерации картинки
    Выведенные отели хранятся в базе данных
    Присваивает начальное состояние выбора команд "command"

    :param call: данные кнопки инлайн клавиатуры в запросе обратного вызова
    :return: None
    '''
    bot.answer_callback_query(call.id)
    user_name = call.from_user.username
    command, date = db_requests.select_command_date(user_name)
    write_information.write_command(command, date, user_name)
    photo_path = BASE_DIR / f'Command. {user_name}.jpg'
    photo = open(photo_path, 'rb')
    bot.send_photo(call.from_user.id, photo=photo)
    hotels = db_requests.select_hotels(user_name)
    write_information.write_hotels(hotels, user_name)
    hotels_photo_path = BASE_DIR / f'Hotels. {user_name}.png'
    hotels_photo = open(hotels_photo_path, 'rb')
    bot.send_photo(call.from_user.id, photo=hotels_photo)
    sleep(3)

    bot.send_message(call.from_user.id, 'Выберете одну из команд:', reply_markup=commands.menu_markup())
    bot.set_state(call.from_user.id, UserInfoState.command)
