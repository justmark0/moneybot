from loader import dp, _, payeer
from keyboards.default.keyboards import *
from keyboards.inline.keyboards import *
from data.models import *
from data.config import *
from states.states import *
from datetime import datetime, timezone


def get_all_locales(message):
    locales = []
    for lang in ALL_LOCALES:
        locales.append(_(message, locale=lang))
    return locales


async def update_all(days):
    for i in range(days):
        users = await User.all()
        for user in users:
            await User.filter(user_id=user.user_id).\
                update(income=(user.money + user.income) * DEPOSIT_COEFFICIENT - user.money)


@dp.message_handler()
async def bot_echo(message: types.Message):
    if message.text in get_all_locales("Put or get money 💳"):
        await message.answer(_("Choose what do you want to do"), reply_markup=put_get_money())
        await Money.next()
    elif message.text in get_all_locales("My account 💼"):
        config_user = await User.get(user_id=1000)
        await update_all((datetime.now(timezone.utc) - config_user.reg_date).days - int(config_user.money))
        await User.filter(user_id=1000).update(money=int((datetime.now(timezone.utc) - config_user.reg_date).days))
        user = await User.get_or_none(user_id=message.chat.id)
        if user is None:
            await message.answer(_("You are not registered use /start"))
            return

        history = payeer.history()

        for transaction_id in history.keys():
            if 'comment' not in history[transaction_id].keys() or "from" not in history[transaction_id].keys():
                continue
            db_transaction = await Transaction.get_or_none(paying_sys_id=transaction_id)
            if db_transaction is not None or (history[transaction_id]['from'] == PAYEER_WALLET_CODE):
                # If transaction exists we do not process it
                continue

            user = await User.get_or_none(user_id=history[transaction_id]['comment'])
            if user:
                bot_pay = True
                if history[transaction_id]['to'] == PAYEER_WALLET_CODE:
                    bot_pay = False
                    await User.filter(user_id=history[transaction_id]['comment']). \
                        update(money=float(user.money) + float(history[transaction_id]['creditedAmount']))

                await Transaction(paying_sys_id=transaction_id, user_id=history[transaction_id]['comment'],
                                  rub_amount=float(history[transaction_id]['creditedAmount']), bot_pay=bot_pay).save()

        user_upd = await User.get_or_none(user_id=message.chat.id)
        days = datetime.now(timezone.utc) - user_upd.reg_date  # Subtracting dates to know for how long user using bot
        await message.answer(_("Your account 🔐\n🔹You have {money} rub on your account\n🔹You can get {take} rub. from your account\n🔹You using this bot {date} days already\n🔹Tomorrow you will have {tomorrow}\n🔹Current deposit coefficient is {coef} %\n🔹You can see your transactions using /transactions").format(
            money=float(user_upd.money) + float(user_upd.income), take=float(user_upd.income),
            date=days.days, tomorrow=(float(user_upd.money) + float(user_upd.income)) * DEPOSIT_COEFFICIENT,
            coef=DEPOSIT_COEFFICIENT * 100), reply_markup=main_keyboard())

    elif message.text in get_all_locales("🇬🇧 Language"):
        await message.answer(_("What language do you want to setup?"), reply_markup=language_keyboard())
        await Language.next()
    else:
        await message.answer(_('Hello! I can help you to easy earn money!'), reply_markup=main_keyboard())
