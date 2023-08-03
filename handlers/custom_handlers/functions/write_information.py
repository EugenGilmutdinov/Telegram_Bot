from PIL import Image, ImageDraw, ImageFont
from config_data.config import BASE_DIR
import textwrap as tw


def write_command(command: str, date_time: str, name: str) -> None:
    '''
    Функция для генерации картинки с информацией о последней выбранной команде пользователем

    :param command: str - выбранная команда пользователем
    :param date_time: str - дата и время выбора команды
    :param name: str - имя пользователя телеграм
    :return: None
    '''
    picture_path = BASE_DIR / 'grey phon (default).jpg'
    img = Image.open(picture_path)
    draw = ImageDraw.Draw(img)
    font_path = BASE_DIR / 'fonts' / 'Comfortaa-Light.ttf'
    font = ImageFont.truetype(f'{font_path}', 40)
    draw.text((200, 257), "Команда:", (255, 255, 255), font=font)
    draw.text((200, 370), "Дата и время\nввода команды:", (255, 255, 255), font=font)
    draw.text((600, 257), command, (255, 255, 255), font=font)
    draw.text((600, 412), date_time, (255, 255, 255), font=font)
    img.save(f"Command. {name}.jpg")


def write_hotels(hotels, name: str) -> None:
    '''
    Функция для генерации картинки с информацией об отелях

    :param hotels: выбранные отели из базы данных
    :param name: str - имя пользователя телеграм
    :return: None
    '''
    picture_path = BASE_DIR / 'phon.png'
    img = Image.open(picture_path)
    draw = ImageDraw.Draw(img)
    font_path = BASE_DIR / 'fonts' / 'Caveat-Bold.ttf'
    font = ImageFont.truetype(f'{font_path}', 28)
    font_hotels_path = BASE_DIR / 'fonts' / 'Caveat-VariableFont_wght.ttf'
    font_hotels = ImageFont.truetype(f'{font_hotels_path}', 24)
    font_stars_path = BASE_DIR / 'fonts' / 'Symbola.ttf'
    font_stars = ImageFont.truetype(f'{font_stars_path}', 24)

    draw.text((100, 18), "Название:", (0, 0, 0), font=font)
    draw.text((330, 18), "Адрес:", (0, 0, 0), font=font)
    draw.text((650, 18), "Расстояние:", (0, 0, 0), font=font)
    draw.text((800, 18), "Цена:", (0, 0, 0), font=font)
    draw.text((920, 18), "Рейтинг:", (0, 0, 0), font=font)
    draw.text((1040, 18), "Звёзды:", (0, 0, 0), font=font)

    x_name, y_name = 64, 67
    x_address, y_address = 330, 67
    x_distance, y_distance = 680, 67
    x_price, y_price = 800, 67
    x_rating, y_rating = 951, 67
    x_stars, y_stars = 1040, 75

    for i, hotel in enumerate(hotels):
        hotel.hotel_name = tw.fill(hotel.hotel_name, width=23)
        hotel.address = tw.fill(hotel.address, width=34)
        hotel.address = hotel.address.replace('None', 'см. название')
        hotel.price = hotel.price.replace('RUB', 'руб')
        hotel.price = hotel.price.replace('USD', 'долл')
        hotel.price = hotel.price.replace('BYN', 'б/руб')
        hotel.rating = hotel.rating.replace('Не указан', '—')
        solid_stars = '★' * int(hotel.stars)  # ★
        outline_stars = '☆' * int(hotel.outline_stars)  # ☆
        stars = f"{solid_stars}{outline_stars}"
        i += 1

        draw.text((x_name, y_name), f"{i}. {hotel.hotel_name}", (0, 0, 0), font=font_hotels)
        draw.text((x_address, y_address), hotel.address, (0, 0, 0), font=font_hotels)
        draw.text((x_distance, y_distance), hotel.distance, (0, 0, 0), font=font_hotels)
        draw.text((x_price, y_price), hotel.price, (0, 0, 0), font=font_hotels)
        draw.text((x_rating, y_rating), hotel.rating, (0, 0, 0), font=font_hotels)
        draw.text((x_stars, y_stars), stars, (0, 0, 0), font=font_stars)

        y_name += 76
        y_address = y_name
        y_distance = y_name
        y_price = y_name
        y_rating = y_name
        y_stars = y_name

    img.save(f"Hotels. {name}.png")

