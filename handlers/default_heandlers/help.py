from loader import bot
from telebot.types import Message
from states.info_for_commands import UserInfoState
from config_data.config import DEFAULT_COMMANDS
from time import sleep
from keyboards.inline import commands


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    '''
    Хэндлер команды 'help'
    Выводит вспомогательную информацию о предоставляемом выборе команд
    Присваивает начальное состояние выбора команд "command"

    :param message: сообщение пользователя
    :return: None
    '''
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.send_message(message.chat.id, '\n'.join(text))
    sleep(3)

    bot.send_message(message.from_user.id, 'Выберете одну из команд:', reply_markup=commands.menu_markup())
    bot.set_state(message.from_user.id, UserInfoState.command)

