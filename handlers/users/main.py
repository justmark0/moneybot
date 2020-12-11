from aiogram import types
from loader import dp, _
from aiogram.dispatcher import FSMContext
from keyboards.inline.keyboards import fkwallet_url
from keyboards.default.keyboards import main_keyboard, language_keyboard
from data.models import User
from data.config import ALL_LOCALES, CANCEL_MESSAGE_LIST, LANGUAGE_DICT
from states.states import Language


def get_all_locales(message):
    locales = []
    for lang in ALL_LOCALES:
        locales.append(_(message, locale=lang))
    return locales


@dp.message_handler(state='*', text=CANCEL_MESSAGE_LIST)
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(_("Main menu"), reply_markup=main_keyboard())


@dp.message_handler(state=Language.NewLanguage)
async def language_setup(message: types.Message, state: FSMContext):
    if message.text not in LANGUAGE_DICT.keys():
        await message.answer(_("Use keyboard to choose options"))
        return
    await User.filter(user_id=message.chat.id).update(language=LANGUAGE_DICT[message.text])
    await message.answer(_("Language was updated successfully"), reply_markup=main_keyboard())
    await state.finish()


@dp.message_handler()
async def bot_echo(message: types.Message):
    if message.text in get_all_locales("Put/Get money 💳"):
        await message.answer(_("You can put money on your account using FKwalet"), reply_markup=fkwallet_url)
    elif message.text in get_all_locales("My account 💼"):
        user = await User.get_or_none(user_id=message.chat.id)
        if user is None:
            await message.answer(_("You are not registered use /start"))
            return
        await message.answer(_("You have {money} rub on your account").format(money=user.money),
                             reply_markup=main_keyboard())
    elif message.text in get_all_locales("🇬🇧 Language"):
        await message.answer(_("What language do you want to setup?"), reply_markup=language_keyboard())
        await Language.next()
    else:
        await message.answer(_('Hello! I can help you to easy earn money!'), reply_markup=main_keyboard())
