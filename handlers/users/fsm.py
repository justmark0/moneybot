from payeer_api import PayeerAPIException
from keyboards.default.keyboards import *
from keyboards.inline.keyboards import *
from data.models import *
from states.states import *
from loader import dp, _, payeer, bot
from handlers.users.messages import get_all_locales
from aiogram.dispatcher import FSMContext
from data.config import LANGUAGE_DICT, MIN_MONEY_OUT, admins, BOT_ALIAS
import re


@dp.message_handler(state=Language.NewLanguage)
async def language_setup(message: types.Message, state: FSMContext):
    if message.text not in LANGUAGE_DICT.keys():
        await message.answer(_("Use keyboard to choose options"))
        return
    await User.filter(user_id=message.chat.id).update(language=LANGUAGE_DICT[message.text])
    await message.answer(_("Language was updated successfully", locale=LANGUAGE_DICT[message.text]),
                         reply_markup=main_keyboard())
    await state.finish()


@dp.message_handler(state=Money.PutGet)
async def select_action(message: types.Message, state: FSMContext):
    if message.text in get_all_locales("Put money 📈"):
        await message.answer(_("You can put money in several ways:"), reply_markup=main_keyboard())
        await message.answer(_("You can choose how do you want to pay"), reply_markup=pay_options())
        await state.finish()
    elif message.text in get_all_locales('Get money 💰'):
        user = await User.get_or_none(user_id=message.chat.id)
        await message.answer(_("Minimal amount of money to get is {min_out} rub. And not earlier than 3 days after bot "
                               "receives money.\n\nFor now you can get {money} rub.\nEnter amount of money you want to"
                               " get:\n(use /cancel to quit)").format(min_out=MIN_MONEY_OUT, money=user.income),
                             reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        await GetMoney.next()
    else:
        await message.answer(_("Use keyboard to choose options"))


@dp.message_handler(state=GetMoney.Amount)
async def select_amount(message: types.message, state: FSMContext):
    if re.fullmatch(r"[+-]?([0-9]*[.])?[0-9]+", message.text):
        user = await User.get_or_none(user_id=message.chat.id)
        if float(message.text) > user.income:
            await message.answer(_("You can get only {money} rub").format(money=user.income))
            return
        if float(message.text) < MIN_MONEY_OUT:
            await message.answer(_("Minimal sum of get from bot is {}").format(MIN_MONEY_OUT))
            return
        async with state.proxy() as data:
            data['amount'] = float(message.text)
        await message.answer(_("Write your payeer wallet number:"))
        await GetMoney.next()
    else:
        await message.answer(_("You can use only numbers"))


@dp.message_handler(state=GetMoney.WalletNumber)
async def select_wallet(message: types.Message, state: FSMContext):
    if re.fullmatch(r"P[a-zA-Z0-9]{7,12}", message.text):
        async with state.proxy() as data:
            data['wallet_code'] = message.text
        await message.answer(_("Do you want to sent {money} rub. to wallet number {wallet}?\n\nWrite \"yes\" to "
                               "confirm.").format(money=data['amount'], wallet=message.text),
                             reply_markup=confirm_keyboard())
        await GetMoney.next()
    else:
        await message.answer(_("It should start with P and contain 7-12 numbers. For example: P1000000"))


@dp.message_handler(state=GetMoney.Finish)
async def finish_check(message: types.Message, state: FSMContext):
    await GetMoney.next()
    if message.text in get_all_locales("yes"):
        async with state.proxy() as data:
            try:
                res = payeer.transfer(data['amount'], data["wallet_code"], "RUB", "RUB", comment=str(message.chat.id))
            except PayeerAPIException as error:
                if str(repr(error)) == "PayeerAPIException(['transferHimselfForbidden'])":
                    await message.answer(_("Write correct data and try again"), reply_markup=main_keyboard())
                else:
                    await message.answer(_("Some error occupied. Try again later"), reply_markup=main_keyboard())
                    for id_a in admins:
                        await bot.send_message(id_a, _("Error occupied in @{}. Description {}").
                                               format(BOT_ALIAS, str(repr(error))))
                return
            await Transaction(paying_sys_id=200, user_id=message.chat.id, rub_amount=data['amount'],
                              bot_pay=True, wallet_number=data["wallet_code"]).save()  # code 200 means it's from bot
            user = await User.get_or_none(user_id=message.chat.id)
            await User.filter(user_id=message.chat.id).update(income=(float(user.income) - float(data['amount'])))
            await message.answer(_("Payment complete. You can check your wallet. Thanks for using our bot!"),
                                 reply_markup=main_keyboard())
    else:
        await message.answer(_("Write \"yes\" to confirm or /cancel to refill data or cancel"))
