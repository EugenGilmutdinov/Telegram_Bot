from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def city_markup(cities: list) -> InlineKeyboardMarkup:
    '''
    Функция для генерации инлайн-клавиатуры с городами

    :param cities: list - список с найденными городами
    :return: InlineKeyboardMarkup - инлайн-клавиатура
    '''
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(text=city['city_name'],
                                              callback_data=f'{city["destination_id"]}'))
    return destinations
