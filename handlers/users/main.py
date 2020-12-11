from aiogram import types
from loader import dp
from loader import _


# TODO learn how to get all locales and do function for it
@dp.message_handler()
async def bot_echo(message: types.Message):
    await message.answer(_('Hello! I can help you to easy earn money!'))
