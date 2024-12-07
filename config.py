from dotenv import load_dotenv
from os import getenv

load_dotenv()

class Config:
    TELEGRAM_KEY = getenv('TELEGRAM_KEY')
    YANDEX_RASP_KEY = getenv('YANDEX_RASP_KEY')
    OPENROUTES_KEY = getenv('OPENROUTES_KEY')