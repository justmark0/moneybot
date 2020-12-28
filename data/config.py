import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
admins = [
    os.getenv("ADMIN_ID"),
]
BOT_ALIAS = os.getenv('BOT_ALIAS')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')

# Database setup
DB_URL = os.getenv("DB_URL")

# Payment settings
DEPOSIT_COEFFICIENT = 1.02
MIN_MONEY_OUT = 400
PEOPLE = 108
SENT_MONEY = os.getenv("SENT_MONEY")
WORKING_FOR = os.getenv("WORKING_FOR")
PAYEER_WALLET_CODE = os.getenv("PAYEER_WALLET_CODE")
PAYEER_API_ID = os.getenv("PAYEER_API_ID")
PAYEER_API_PASS = os.getenv("PAYEER_API_PASS")

# Middleware / Locales setup
ALL_LOCALES = ['ru', 'en']
CANCEL_MESSAGE_LIST = ["⬅️ Отмена", "⬅️ Cancel"]
LANGUAGE_DICT = {"🇷🇺 Русский": 'ru', "🇬🇧 English": 'en'}
I18N_DOMAIN = 'bot'
BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = BASE_DIR / 'locales'
