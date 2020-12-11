from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp
from loader import _
from loader import dp
from utils.misc import rate_limit


@rate_limit(5, 'help')
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    await message.answer(_("Hello! I can help you to earn money! Just send me money and you will get more in "
                         "few days!\nList of commands:\n/start - Restart dialog\n/help - See list of commands"))
