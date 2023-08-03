import re
from telebot import types
from telebot import TeleBot
from telebot.custom_filters import AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
from datetime import datetime

calendar_factory = CallbackData("year", "month", prefix="calendar")
calendar_factory_ch_day = CallbackData("year", "month", "day", prefix="calendar")
calendar_zoom = CallbackData("year", prefix="calendar_zoom")


def first_date_check(call) -> bool:
    '''
    Функция для проверки даты въезда на соответствие шаблону

    :param call: Any
    :return: bool
    '''
    try:
        datetime.strptime(call, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def full_date_check(call) -> bool:
    '''
    Функция для проверки полной даты на соответствие шаблону

    :param call: Any
    :return: bool
    '''
    try:
        date_pattern = r'\d{4}-\d{2}-\d{2}, \d{4}-\d{2}-\d{2}'
        if re.search(date_pattern, call):
            return True
    except Exception:
        return False


class CalendarCallbackFilter(AdvancedCustomFilter):
    '''
    Класс фильтр коллбэк

    Attributes:
        key : конфигуратор календаря

    '''
    key = 'calendar_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class CalendarZoomCallbackFilter(AdvancedCustomFilter):
    '''
    Класс фильтр инлайн-кнопки "Отдалить"

    Attributes:
        key : конфигуратор инлайн-кнопки "Отдалить"

    '''
    key = 'calendar_zoom_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


def bind_filters(bot: TeleBot) -> None:
    '''
    Связующие фильтры

    :param bot: TeleBot
    :return: None
    '''
    bot.add_custom_filter(CalendarCallbackFilter())
    bot.add_custom_filter(CalendarZoomCallbackFilter())