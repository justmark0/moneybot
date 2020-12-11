from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import _
from loader import dp
from keyboards.default.keyboards import main_keyboard
from data.models import User


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    user = await User.get_or_none(user_id=message.chat.id)
    if user is None:
        await User(user_id=message.chat.id, alias=message.from_user.username, money=0, language="en").save()
    await message.answer(_('Hello! I can help you to easy earn money!'), reply_markup=main_keyboard())
