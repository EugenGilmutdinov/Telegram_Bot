from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def photo_output() -> ReplyKeyboardMarkup:
    '''
    Функция для генерации риплай-клавиатуры с выбором вывода фотографий (да/нет)

    :return: ReplyKeyboardMarkup - риплай-клавиатура
    '''
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn1 = KeyboardButton('Да')
    itembtn2 = KeyboardButton('Нет')
    keyboard.add(itembtn1, itembtn2)
    return keyboard
