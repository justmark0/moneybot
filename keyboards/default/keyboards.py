from aiogram import types
from loader import _


def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard_text = (_("Put or get money 💳"), _('My account 💼'), _('🇬🇧 Language'))
    keyboard.add(*(types.KeyboardButton(text) for text in keyboard_text))
    return keyboard


def language_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard_text = ('🇷🇺 Русский', '🇬🇧 English', _("⬅️ Cancel"))
    keyboard.add(*(types.KeyboardButton(text) for text in keyboard_text))
    return keyboard


def put_get_money():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard_text = (_('Put money 📈'), _('Get money 💰'), _("⬅️ Cancel"))
    keyboard.add(*(types.KeyboardButton(text) for text in keyboard_text))
    return keyboard


def confirm_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard_text = (_('yes'), _("⬅️ Cancel"))
    keyboard.add(*(types.KeyboardButton(text) for text in keyboard_text))
    return keyboard
