from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from middlewares import setup
from data.config import *
from data.models import Translations
from payeer_api import PayeerAPI


def T(message):
    translation = await Translations.get_or_none(ru=message)
    if translation is not None:
        return translation.en
    return message


bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

payeer = PayeerAPI(PAYEER_WALLET_CODE, PAYEER_API_ID, PAYEER_API_PASS)

i18n = setup(dp)
_ = i18n.gettext
