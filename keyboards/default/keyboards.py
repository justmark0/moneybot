from aiogram import types
from loader import _


def main_keyboard(locale=None):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if locale is None:
        keyboard_text = (_("Пополнить или снять деньги 💳"), _("Мой аккаунт 💼"), _("Инфо 📈"), _("🇷🇺 Язык"))
    else:
        keyboard_text = (_("Пополнить или снять деньги 💳", locale=locale), _("Мой аккаунт 💼", locale=locale),
                         _("Инфо 📈", locale=locale), _("🇷🇺 Язык", locale=locale))
    keyboard.add(*(types.KeyboardButton(text) for text in keyboard_text))
    return keyboard


def language_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard_text = ('🇷🇺 Русский', '🇬🇧 English', _("⬅️ Отмена"))
    keyboard.add(*(types.KeyboardButton(text) for text in keyboard_text))
    return keyboard


def put_get_money():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard_text = (_("Пополнить счет 💳"), _("Снять деньги 💰"), _("⬅️ Отмена"))
    keyboard.add(*(types.KeyboardButton(text) for text in keyboard_text))
    return keyboard


def confirm_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard_text = (_('да'), _("⬅️ Отмена"))
    keyboard.add(*(types.KeyboardButton(text) for text in keyboard_text))
    return keyboard
