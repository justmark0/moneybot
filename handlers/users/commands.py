from aiogram.dispatcher import FSMContext
from loader import dp, _
from keyboards.default.keyboards import *
from keyboards.inline.keyboards import *
from data.models import *
from data.config import CANCEL_MESSAGE_LIST
from utils.misc import rate_limit
from datetime import datetime, timezone


@dp.message_handler(state='*', text=CANCEL_MESSAGE_LIST)
@dp.message_handler(state='*', commands=['cancel'])
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(_("Главное меню"), reply_markup=main_keyboard())


@rate_limit(5, 'help')
@dp.message_handler(state="*", commands=["help"])
async def bot_help(message: types.Message):
    await message.answer(_("Привет! Я помогу тебе зарабатывать! Просто отправь мне деньги и через "
                           "пару дней получишь больше!\n"
                           "Список комманд:\n"
                           "/start - Перезапустить бота\n"
                           "/help - Посмотреть список комманд\n"
                           "/transactions - Посмотреть историю ваших транзакций"))


@dp.message_handler(state="*", commands=["start"])
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    user = await User.get_or_none(user_id=message.chat.id)
    if user is None:
        await User(user_id=message.chat.id, alias=message.from_user.username, money=0, language="ru").save()
    await message.answer(_("Привет! Я помогу тебе заработать деньги!"), reply_markup=main_keyboard())


@dp.message_handler(state="*", commands=['transactions'])
async def bot_start(message: types.Message, state):
    await state.finish()
    transactions_query = await Transaction.filter(user_id=message.chat.id)
    if transactions_query is not None:
        message_text = _("Вот лист ваших транзакций:\n")
        for transaction in transactions_query:
            days = datetime.now(timezone.utc) - transaction.date
            if transaction.bot_pay:
                message_text += _("🔸Бот отправил {} рублей на {} Payeer кошелек {} дней назад\n"). \
                    format(transaction.rub_amount, transaction.wallet_number, days.days)
            else:
                message_text += _("🔹Вы перевели боту {} рублей {} дней назад\n"). \
                    format(transaction.rub_amount, days.days)
        await message.answer(message_text, reply_markup=main_keyboard())
    else:
        await message.answer(_("У вас еще нет транзакций"))
