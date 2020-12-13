from loader import dp, _
from keyboards.default.keyboards import *
from keyboards.inline.keyboards import *
from data.models import *
from data.config import ALL_LOCALES
from states.states import *
from datetime import datetime, timezone


def get_all_locales(message):
    locales = []
    for lang in ALL_LOCALES:
        locales.append(_(message, locale=lang))
    return locales


@dp.message_handler()
async def bot_echo(message: types.Message):
    if message.text in get_all_locales("Put or get money 💳"):
        await message.answer(_("Choose what do you want to do"), reply_markup=put_get_money())
        await Money.next()
    elif message.text in get_all_locales("My account 💼"):
        user = await User.get_or_none(user_id=message.chat.id)
        if user is None:
            await message.answer(_("You are not registered use /start"))
            return

        days = datetime.now(timezone.utc) - user.reg_date  # Subtracting dates to know for how long user using bot
        await message.answer(_("Your account 🔐\n🔹You have {money} rub on your account\n🔹You using this bot {date} "
                               "days already\n\nYou can see your transactions using /transactions").format(
            money=user.money, date=days.days), reply_markup=main_keyboard())
    elif message.text in get_all_locales("🇬🇧 Language"):
        await message.answer(_("What language do you want to setup?"), reply_markup=language_keyboard())
        await Language.next()
    else:
        await message.answer(_('Hello! I can help you to easy earn money!'), reply_markup=main_keyboard())
