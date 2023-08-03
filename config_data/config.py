import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('lowprice', "Топ самых дешёвых отелей в городе"),
    ('highprice', "Топ самых дорогих отелей в городе"),
    ('bestdeal', "Отели, наиболее подходящие по цене и расположению от центра"),
    ('history', "История поиска отелей")
)
