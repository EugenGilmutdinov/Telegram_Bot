from loader import bot
from telebot.types import Message
from states.info_for_commands import UserInfoState
from database import *
from config_data.config import BASE_DIR
from keyboards.inline import commands
from time import sleep

from handlers.custom_handlers.functions import write_information


@bot.message_handler(commands=['history'])
def show_history(message: Message) -> None:
    '''
    Хэндлер команды 'history'
    Выводит информацию об уже показанных отелях, повторно выводя их на экран при помощи генерации картинки
    Выведенные отели хранятся в базе данных
    Присваивает начальное состояние выбора команд "command"

    :param message: сообщение пользователя
    :return: None
    '''
    user_name = message.from_user.username
    command, date = db_requests.select_command_date(user_name)
    write_information.write_command(command, date, user_name)
    photo_path = BASE_DIR / f'Command. {user_name}.jpg'
    photo = open(photo_path, 'rb')
    bot.send_photo(message.chat.id, photo=photo)
    hotels = db_requests.select_hotels(user_name)
    write_information.write_hotels(hotels, user_name)
    hotels_photo_path = BASE_DIR / f'Hotels. {user_name}.png'
    hotels_photo = open(hotels_photo_path, 'rb')
    bot.send_photo(message.chat.id, photo=hotels_photo)
    sleep(3)

    bot.send_message(message.from_user.id, 'Выберете одну из команд:', reply_markup=commands.menu_markup())
    bot.set_state(message.from_user.id, UserInfoState.command)

