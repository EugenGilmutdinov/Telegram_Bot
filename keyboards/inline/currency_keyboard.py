from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def currency_markup() -> InlineKeyboardMarkup:
    '''
    Функция для генерации инлайн-клавиатуры с выбором валюты

    :return: InlineKeyboardMarkup - инлайн-клавиатура
    '''
    keyboard = InlineKeyboardMarkup(row_width=3)
    usd_button = InlineKeyboardButton(text="USD", callback_data="USD")
    rub_button = InlineKeyboardButton(text="RUB", callback_data="RUB")
    byn_button = InlineKeyboardButton(text="BYN", callback_data="BYN")
    keyboard.add(usd_button, rub_button, byn_button)
    return keyboard
