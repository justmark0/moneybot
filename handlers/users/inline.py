from aiogram.types import ParseMode
from loader import dp, _
from data.config import PAYEER_WALLET_CODE
from aiogram import types


@dp.callback_query_handler(text='payeer')
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    await query.message.edit_text(_("💰*Для пополнения вашего баланса переведите нужную сумму на кошелек "
                                    "Payeer:* `{wallet}`\n"
                                    "В комментарии платежа ОБЯЗАТЕЛЬНО напишите число: `{code}` и пополняйте"
                                    " ТОЛЬКО *рублевым* счетом\. Если Вы не напишете это число мы не сможем"
                                    " пополнить Ваш баланс\!В течении минуты ваш счет обновится\.\n"
                                    "https://payeer\.com/"
                                    ).
                                  format(wallet=PAYEER_WALLET_CODE, code=query.message.chat.id),
                                  parse_mode=ParseMode.MARKDOWN_V2)
