from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import _
from loader import dp


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(_('Привет, {name}!').format(name=message.from_user.full_name))
