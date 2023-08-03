import re
import json

from loguru import logger
from telebot import types
from datetime import date
from operator import itemgetter


def show_hotels(res) -> dict:
    '''
    Функция для составления информации об отелях

    :param res: ответ АPI Hotel (словарь с данными об отелях)
    :return: dict - словарь, с отелями
    '''
    hotels_pattern = r'(?<=,)"results":.+?(?=,"pagination)'
    hotels_info = re.search(hotels_pattern, res.text)
    suggestions = json.loads(f"{{{hotels_info[0]}}}")
    with open("hotels_dict.json", "w", encoding='utf-8') as file:
        json.dump(suggestions["results"], file, indent=4, ensure_ascii=False)
    hotels_dict = dict()
    for hotel in suggestions["results"]:
        try:
            hotels_dict = {
                "id": hotel.get('id'),
                "name": hotel.get('name'),
                "starRating": hotel.get('starRating'),
                "distance from": hotel["landmarks"][0].get("label"),
                "distance": hotel["landmarks"][0]["distance"][:3],
                "streetAddress": hotel['address'].get('streetAddress'),
                "locality": hotel['address'].get('locality'),
                "countryName": hotel['address'].get('countryName'),
                "coordinate": hotel.get('coordinate')
            }
            if hotel.get('guestReviews'):
                hotels_dict["rating"] = hotel['guestReviews'].get('rating')
            if not hotel.get('guestReviews'):
                logger.info(f"Отель: {hotel.get('name')} не имеет рейтинга")
                hotels_dict["rating"] = "Не указан"
            if hotel['address'].get('extendedAddress'):
                hotels_dict["extendedAddress"] = hotel['address'].get('extendedAddress')
            if not hotel['address'].get('extendedAddress'):
                logger.info(f"Отель: {hotel.get('name')} не имеет расширенного адреса")
                hotels_dict["extendedAddress"] = ""
            if hotel['address'].get('region'):
                hotels_dict["region"] = hotel['address'].get('region')
            if not hotel['address'].get('region'):
                logger.info(f"Отель: {hotel.get('name')} не имеет региона")
                hotels_dict["region"] = ""
            if hotel['ratePlan']['price'].get('exactCurrent'):
                hotels_dict["price"] = hotel['ratePlan']['price'].get('exactCurrent')
            if not hotel['ratePlan']['price'].get('exactCurrent'):
                logger.info(f"Отель: {hotel.get('name')} не имеет цены")
                hotels_dict["price"] = ""
        except KeyError:
            continue
        finally:
            yield hotels_dict


def show_hotels_bestdeal(res, distance: list) -> list or None:
    '''
    Функция для составления информации об отелях для команды bestdeal

    :param res: ответ АPI Hotel (словарь с данными об отелях)
    :param distance: list - список диапазона расстояния, выбранного пользователем
    :return: list or None
    '''
    hotels_list = []
    min_dist = distance[0]
    max_dist = distance[1]
    for i, hotel in enumerate(res):
        try:
            distance = hotel["landmarks"][0]['distance'].replace(',', '.')
            hotels_list.append(
                {
                    "id": hotel.get('id'),
                    "name": hotel.get('name'),
                    "starRating": hotel.get('starRating'),
                    "distance from": hotel["landmarks"][0].get("label"),
                    "distance": float(distance[:3]),
                    "streetAddress": hotel['address'].get('streetAddress'),
                    "locality": hotel['address'].get('locality'),
                    "countryName": hotel['address'].get('countryName'),
                    "coordinate": hotel.get('coordinate')
                }
            )
            if hotel.get('guestReviews'):
                hotels_list[i]["rating"] = hotel['guestReviews'].get('rating')
            if not hotel.get('guestReviews'):
                logger.info(f"Отель: {hotel.get('name')} не имеет рейтинга")
                hotels_list[i]["rating"] = "Не указан"
            if hotel['address'].get('extendedAddress'):
                hotels_list[i]["extendedAddress"] = hotel['address'].get('extendedAddress')
            if not hotel['address'].get('extendedAddress'):
                logger.info(f"Отель: {hotel.get('name')} не имеет расширенного адреса")
                hotels_list[i]["extendedAddress"] = ""
            if hotel['address'].get('region'):
                hotels_list[i]["region"] = hotel['address'].get('region')
            if not hotel['address'].get('region'):
                logger.info(f"Отель: {hotel.get('name')} не имеет региона")
                hotels_list[i]["region"] = ""
            if hotel['ratePlan']['price'].get('exactCurrent'):
                hotels_list[i]["price"] = hotel['ratePlan']['price'].get('exactCurrent')
            if not hotel['ratePlan']['price'].get('exactCurrent'):
                logger.info(f"Отель: {hotel.get('name')} не имеет цены")
                hotels_list[i]["price"] = ""
        except KeyError:
            continue
    hotels_filter = list(filter(lambda x: min_dist <= x['distance'] <= max_dist, hotels_list))
    hotels_sorted = sorted(hotels_filter, key=itemgetter('price', 'distance'))
    if hotels_sorted:
        return hotels_sorted
    else:
        logger.info("При фильтрации и сортировке отелей не найдено")
        return None


def show_hotel_info(hotel: dict, data: dict, currency: float) -> str:
    '''
    Функция для составления сообщения с информацией об отеле

    :param hotel: dict - словарь с отелем
    :param data: dict - словарь хранения данных о выборе пользователя
    :param currency: ответ Api валют
    :return: str - сообщение с информацией об отеле
    '''
    solid_stars = '★' * int(hotel['starRating'])  # ★
    outline_stars = '☆' * (5 - int(hotel['starRating']))  # ☆
    curr = data['currency']
    distance = hotel["distance"]
    list_checkIn = str(data['checkIn']).split('-')
    list_checkOut = str(data['checkOut']).split('-')
    year1, month1, day1 = list(map(lambda x: int(x), list_checkIn))
    year2, month2, day2 = list(map(lambda x: int(x), list_checkOut))
    str_checkIn = date(year=year1, month=month1, day=day1).strftime('%d.%m.%Y')
    str_checkOut = date(year=year2, month=month2, day=day2).strftime('%d.%m.%Y')
    if "BYN" in data['currency']:
        hotel['price'] = round(float(hotel['price']) * float(currency), 2)
        curr = data['currency'][1]
    if data['command'] == '/bestdeal':
        distance = str(distance).replace('.', ',')
    full_price = round(hotel['price'] * int(data['num_days']), 2)
    hotel_info = f"<strong>Название:</strong> {hotel['name']}\n" \
                 f"<strong>Кол-во звёзд:</strong> {solid_stars}{outline_stars}\n" \
                 f"<strong>Рейтинг:</strong> {hotel['rating']}\n" \
                 f"<strong>Дата въезда:</strong> {str_checkIn}\n" \
                 f"<strong>Дата выезда:</strong> {str_checkOut}\n" \
                 f"<strong>Адрес:</strong> {hotel['streetAddress']} {hotel['extendedAddress']}\n{hotel['locality']}, " \
                 f"{hotel['region']} {hotel['countryName']}\n" \
                 f'<strong>Расстояние от:</strong> "{hotel["distance from"]}" - {distance} км\n' \
                 f"<strong>Цена за сутки:</strong> {hotel['price']} {curr}" \
                 f"\n<strong>Цена за весь период ({data['num_days']} дней):</strong> {full_price} {curr}"
    return hotel_info


def photos(res, num_photos: int, caption: str, hotels_numb: int) -> list:
    '''
    Функция для составления списка со ссылками на фото отеля

    :param res: ответ АPI Hotel (словарь с данными об отелях)
    :param num_photos: int - количество фотографий, выбранное пользователем
    :param caption: str - подпись с информацией об отеле
    :param hotels_numb: int - нумерация отеля
    :return: list - список со ссылками на фото отеля
    '''
    photos_pattern = r'(?<=,)"hotelImages":.+?(?=,"featuredImageTrackingDetails")'

    hotel_photos = re.search(photos_pattern, res.text)

    suggestions = json.loads(f"{{{hotel_photos[0]}}}")
    photos_list = list()
    for i, photo in enumerate(suggestions["hotelImages"]):
        url = str(photo['baseUrl'])
        url_photo = url.replace("{size}", "z")
        if i == 0:
            url_photo = types.InputMediaPhoto(url_photo, caption=f'<strong>{hotels_numb}.</strong>\n{caption}',
                                              parse_mode='html')
        else:
            url_photo = types.InputMediaPhoto(url_photo)
        photos_list.append(url_photo)
        if i == (num_photos - 1):
            break
    return photos_list
