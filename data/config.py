import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
admins = [
    os.getenv("ADMIN_ID"),
]

# Database setup
DB_URL = os.getenv("DB_URL")

# Middleware setup
I18N_DOMAIN = 'bot'
BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = BASE_DIR / 'locales'
