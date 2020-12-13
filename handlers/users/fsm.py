from keyboards.default.keyboards import *
from keyboards.inline.keyboards import *
from data.models import *
from states.states import *
from loader import dp, _
from handlers.users.messages import get_all_locales
from aiogram.dispatcher import FSMContext
from data.config import LANGUAGE_DICT


@dp.message_handler(state=Language.NewLanguage)
async def language_setup(message: types.Message, state: FSMContext):
    if message.text not in LANGUAGE_DICT.keys():
        await message.answer(_("Use keyboard to choose options"))
        return
    await User.filter(user_id=message.chat.id).update(language=LANGUAGE_DICT[message.text])
    await message.answer(_("Language was updated successfully", locale=LANGUAGE_DICT[message.text]),
                         reply_markup=main_keyboard())
    await state.finish()


@dp.message_handler(state=Money.PutGet)
async def language_setup(message: types.Message, state: FSMContext):
    if message.text in get_all_locales("Put money 📈"):
        await message.answer(_("You can put money in several ways:"), reply_markup=main_keyboard())
        await message.answer(_("You can choose how do you want to pay"), reply_markup=pay_options())
        await state.finish()
    elif message.text in get_all_locales('Get money 💰'):

        await state.finish()
        await GetMoney.next()
    else:
        await message.answer(_("Use keyboard to choose options"))
