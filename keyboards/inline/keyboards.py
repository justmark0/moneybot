from aiogram import types


def pay_options():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    text_and_data = (
        ('Payeer', 'payeer'),
    )
    keyboard.add(*(types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data))
    return keyboard
