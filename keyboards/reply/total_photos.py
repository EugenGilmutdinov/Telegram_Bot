from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def total_hotels() -> ReplyKeyboardMarkup:
    '''
    Функция для генерации риплай-клавиатуры с выбором количества фотографий отеля

    :return: ReplyKeyboardMarkup - риплай-клавиатура
    '''
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
    buttons = [KeyboardButton(str(i)) for i in range(1, 11)]
    keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4])
    keyboard.add(buttons[5], buttons[6], buttons[7], buttons[8], buttons[9])
    return keyboard
