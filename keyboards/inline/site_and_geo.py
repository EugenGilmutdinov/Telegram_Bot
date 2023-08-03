from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def site_location_markup(site: str, location: dict) -> InlineKeyboardMarkup:
    '''
    Функция для генерации инлайн-клавиатуры с кнопками сайта и месторасположения отеля

    :param site: str - url-адрес отеля
    :param location: dict - координаты отеля
    :return: InlineKeyboardMarkup - инлайн-клавиатура
    '''
    keyboard = InlineKeyboardMarkup(row_width=2)
    site_button = InlineKeyboardButton(text="Сайт", url=f"https://www.hotels.com/ho{site}")
    location_button = InlineKeyboardButton(text="Расположение",
                                           url=f"https://maps.yandex.by/?text={location['lat']}+{location['lon']}")
    keyboard.add(site_button, location_button)
    return keyboard
