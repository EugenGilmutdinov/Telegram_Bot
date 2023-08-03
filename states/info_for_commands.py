from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    '''
    Класс, хранящий данные введенные пользователем

    Attributes:
        command: команда, выбранная пользователем
        city: город, выбранный пользователем
        price_range: диапазон цен
        distance_range: диапазон расстояния
        checkIn: дата въезда, выбранная пользователем
        checkOut: дата выезда, выбранная пользователем
        checkIn_Out: дата въезда и выезда
        num_hotels: количество отелей, выбранное пользователем
        currency: валюта, выбранная пользователем
        display_result_bestdeal: состояние вывода подходящих отелей для команды "bestdeal"
        display_result: состояние вывода подходящих отелей
        get_photos_bestdeal: состояние вывода фотографий отелей для команды "bestdeal"
        get_photos: состояние вывода фотографий отелей

    '''
    command = State()
    city = State()
    price_range = State()
    distance_range = State()
    checkIn = State()
    checkOut = State()
    checkIn_Out = State()
    num_hotels = State()
    currency = State()
    display_result_bestdeal = State()
    display_result = State()
    get_photos_bestdeal = State()
    get_photos = State()
