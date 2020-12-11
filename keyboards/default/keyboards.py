from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types
from loader import _

main_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
main_keyboard_text = (_('Put money 💳'), _('My account 💼'), _('🇬🇧 Language'))
main_keyboard.add(*(types.KeyboardButton(text) for text in main_keyboard_text))

