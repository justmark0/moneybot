from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from middlewares import setup
from data.config import *
# from data.models import Translations
from payeer_api import PayeerAPI
# from utils.misc.logging import logging


# async def T(code, lang='ru'):  # Function for translations from database
#     translation = await Translations.get_or_none(code=code)
#     if translation is None:
#         logging.error(f"Fill translation in database for code: {code}")
#         raise
#     if lang == "ru":
#         return translation.ru
#     return translation.en


bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

payeer = PayeerAPI(PAYEER_WALLET_CODE, PAYEER_API_ID, PAYEER_API_PASS)

i18n = setup(dp)
_ = i18n.gettext
