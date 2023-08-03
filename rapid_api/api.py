import os
import http.client
import requests
import re
import json
import textwrap

from loguru import logger
from keyboards.inline import finding_city
from telebot.types import InlineKeyboardMarkup

conn = http.client.HTTPSConnection("hotels4.p.rapidapi.com")

url_search = "https://hotels4.p.rapidapi.com/locations/v2/search"

api_rub_currency = "https://www.nbrb.by/api/exrates/rates/456"

url_hotels = "https://hotels4.p.rapidapi.com/properties/list"

search_price_url = "https://hotels4.p.rapidapi.com/properties/get-details"

url_hotel_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": os.getenv('RAPID_API_KEY')
}


def request_to_api_currency(url: str = api_rub_currency) -> float:
    '''
    Функция для запроса к API валют

    :param url: str - url-адрес стоимости российского рубля
    :return: float - округленная стоимость в белорусских рублях
    '''
    try:
        response = requests.request("GET", url)
        if response.status_code == requests.codes.ok:
            currency = response.json()
            currency = round(currency.get("Cur_OfficialRate") / 100, 4)
            return currency
    except Exception:
        logger.error("Возникли проблемы с API валют")


def request_to_api(url: str, headers: dict, querystring: dict):
    '''
    Функция для запроса к Hotels API

    :param url: str - url-адрес
    :param headers: dict - словарь с идентификационными данными
    :param querystring: dict - словарь с параметрами поиска
    :return:
    '''
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        if response.status_code == requests.codes.ok:
            return response
    except Exception:
        logger.error("Возникли проблемы с Hotels API")


def request_to_city(city: str) -> InlineKeyboardMarkup or None:
    '''
    Функция запроса к Hotels API для поиска отелей в данном городе

    :param city: str - город поиска отелей
    :return: InlineKeyboardMarkup or None - инлайн-клавиатуру либо ничего
    '''
    querystring = {"query": f"{city}", "locale": "ru_RU", "currency": "RUB"}
    response = request_to_api(url=url_search, headers=headers, querystring=querystring)
    try:
        response_text = json.loads(response.text)
        city = response_text['suggestions'][0]['entities']
        if city:
            pattern = r'(?<="CITY_GROUP",).+?[\]]'
            find = re.search(pattern, response.text)
            suggestions = dict()
            if find:
                suggestions = json.loads(f"{{{find[0]}}}")
            cities = list()
            for dest_id in suggestions['entities']:  # Обрабатываем результат
                clear_destination = re.sub('<[^>]*>', '', dest_id['caption'])
                clear_destination = textwrap.fill(clear_destination, 43)
                cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
            cities_keyboards = finding_city.city_markup(cities)
            return cities_keyboards
    except KeyError:
        return None


def request_to_hotels(data: dict):
    '''
    Функция запроса к Hotels API для поиска подходящих отелей

    :param data: dict - словарь хранения данных о выборе пользователя
    :return:
    '''
    querystring = {"destinationId": data['city'], "pageNumber": "1", "pageSize": data['num_hotels'],
                   "checkIn": data['checkIn'], "checkOut": data['checkOut'],
                   "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU",
                   "currency": data['currency']}
    if data['command'] == "/highprice":
        querystring["sortOrder"] = "PRICE_HIGHEST_FIRST"
    if data['command'] == "/bestdeal":
        querystring["priceMin"] = data['price_range'][0]
        querystring["priceMax"] = data['price_range'][1]
        querystring["sortOrder"] = "DISTANCE_FROM_LANDMARK"
    if "BYN" in data['currency']:
        querystring["currency"] = data['currency'][0]
    response = request_to_api(url=url_hotels, headers=headers, querystring=querystring)
    return response


def request_to_photos(hotels_id: int):
    '''
    Функция запроса к Hotels API для поиска фотографий

    :param hotels_id: int - id-отеля
    :return:
    '''
    photo_querystring = {"id": str(hotels_id)}
    response_photos = request_to_api(url=url_hotel_photos, headers=headers, querystring=photo_querystring)
    return response_photos


def checking_response(res) -> dict or None:
    '''
    Функция проверки запроса для поиска по шаблону касательно команды "bestdeal"

    :param res: Any
    :return: dict or None
    '''
    hotels_pattern = r'(?<=,)"results":.+?(?=,"pagination)'
    hotels_info = re.search(hotels_pattern, res.text)
    if hotels_info:
        suggestions = json.loads(f"{{{hotels_info[0]}}}")
        return suggestions['results']
    else:
        return None
