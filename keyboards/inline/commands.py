from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def menu_markup() -> InlineKeyboardMarkup:
    '''
    Функция для генерации инлайн-клавиатуры с главным меню

    :return: InlineKeyboardMarkup - инлайн-клавиатура
    '''
    keyboard = InlineKeyboardMarkup(row_width=2)
    lowprice_btn = InlineKeyboardButton(text="lowprice", callback_data="/lowprice")
    highprice_btn = InlineKeyboardButton(text="highprice", callback_data="/highprice")
    bestdeal_btn = InlineKeyboardButton(text="bestdeal", callback_data="/bestdeal")
    history_btn = InlineKeyboardButton(text="history", callback_data="/history")
    help_btn = InlineKeyboardButton(text="help", callback_data="/help")
    keyboard.add(lowprice_btn, highprice_btn, bestdeal_btn, history_btn, help_btn)
    return keyboard
