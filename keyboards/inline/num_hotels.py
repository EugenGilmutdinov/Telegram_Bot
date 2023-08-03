from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def total_hotels() -> InlineKeyboardMarkup:
    '''
    Функция для генерации инлайн-клавиатуры с выбором количества отелей

    :return: InlineKeyboardMarkup - инлайн-клавиатура
    '''
    keyboard = InlineKeyboardMarkup(row_width=5)
    buttons = [InlineKeyboardButton(text=i, callback_data=i) for i in range(1, 11)]
    keyboard.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4])
    keyboard.add(buttons[5], buttons[6], buttons[7], buttons[8], buttons[9])
    return keyboard
