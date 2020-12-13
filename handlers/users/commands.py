from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp, _
from keyboards.default.keyboards import *
from keyboards.inline.keyboards import *
from data.models import *
from data.config import CANCEL_MESSAGE_LIST
from aiogram.dispatcher.filters.builtin import CommandHelp
from utils.misc import rate_limit
from handlers.users.messages import get_all_locales


@dp.message_handler(state='*', text=CANCEL_MESSAGE_LIST)
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(_("Main menu"), reply_markup=main_keyboard())


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    await message.answer(_("Hello! I can help you to earn money! Just send me money and you will get more in "
                           "few days!\nList of commands:\n/start - Restart dialog\n/help - See list of commands"
                           "\n/transactions - See list of your transactions"))


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    user = await User.get_or_none(user_id=message.chat.id)
    if user is None:
        await User(user_id=message.chat.id, alias=message.from_user.username, money=0, language="en").save()
    await message.answer(_('Hello! I can help you to easy earn money!'), reply_markup=main_keyboard())


@dp.message_handler(state="*", commands=['transactions'])
async def bot_start(message: types.Message, state):
    await state.fiinish()
    await message.answer("Will be added a bit later")
    # TODO make transactions
