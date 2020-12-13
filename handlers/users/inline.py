from loader import dp, _
from data.config import PAYEER_WALLET_CODE
from aiogram import types


@dp.callback_query_handler(text='payeer')
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    await query.message.edit_text(_("**To put money in bot send amount of money you want to Payeer wallet:** __{wallet"
                                    "}__\nIT is NECESSARILY to write {code} in comments and send ONLY rubles. Your "
                                    "account will not receive money if you will not do this.   In a minute your "
                                    "account deposit will update.\nhttps://payeer.com/").
                                  format(wallet=PAYEER_WALLET_CODE, code=query.message.chat.id), parse_mode="Markdown")
