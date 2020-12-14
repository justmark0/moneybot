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
        await message.answer(_("Используйте клавиатуру чтобы выбрать возможные опции"))
        return
    await User.filter(user_id=message.chat.id).update(language=LANGUAGE_DICT[message.text])
    await message.answer(_("Язык был обновлен", locale=LANGUAGE_DICT[message.text]),
                         reply_markup=main_keyboard(locale=LANGUAGE_DICT[message.text]))
    await state.finish()


@dp.message_handler(state=Money.PutGet)
async def select_action(message: types.Message, state: FSMContext):
    if message.text in get_all_locales("Пополнить счет 💳"):
        await message.answer(_("Вы можете пополнить счет несколькими способами:"), reply_markup=main_keyboard())
        await message.answer(_("Можете выбрать ниже какими способами пополнить счет"), reply_markup=pay_options())
        await state.finish()
    elif message.text in get_all_locales("Снять деньги 💰"):
        user = await User.get_or_none(user_id=message.chat.id)
        await message.answer(_("Минимальная сумма вывода {min_out} рублей\nВы можете вывести {money} рублей.\nВведите "
                               "сумму которую хотите вывести:\n\n(можете исползовать /cancel чтобы выйти)").
                             format(min_out=MIN_MONEY_OUT, money=user.income), reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        await GetMoney.next()
    else:
        await message.answer(_("Используйте клавиатуру чтобы выбрать возможные опции"))


@dp.message_handler(state=GetMoney.Amount)
async def select_amount(message: types.message, state: FSMContext):
    if re.fullmatch(r"[+-]?([0-9]*[.])?[0-9]+", message.text):
        user = await User.get_or_none(user_id=message.chat.id)
        if float(message.text) > user.income:
            await message.answer(_("Вы можете вывести только {money} рублей").format(money=user.income))
            return
        if float(message.text) < MIN_MONEY_OUT:
            await message.answer(_("Минимальная сумма которую можно вывести из бота {} рублей").format(MIN_MONEY_OUT))
            return
        async with state.proxy() as data:
            data['amount'] = float(message.text)
        await message.answer(_("Введите ваш номер вашего Payeer кошелька"))
        await GetMoney.next()
    else:
        await message.answer(_("Вы можете использовать только цифры"))


@dp.message_handler(state=GetMoney.WalletNumber)
async def select_wallet(message: types.Message, state: FSMContext):
    if re.fullmatch(r"P[a-zA-Z0-9]{7,12}", message.text):
        async with state.proxy() as data:
            data['wallet_code'] = message.text
        await message.answer(_("Вы уверены что хотите выслать {money} рублей на кошелек {wallet}?\n\nНапишите \"да\" "
                               "чтобы подтвердить.").format(money=data['amount'], wallet=message.text),
                             reply_markup=confirm_keyboard())
        await GetMoney.next()
    else:
        await message.answer(_("Номер кошелька начинается с P и содержит 7-12 цифр. Например P1000000"))

#TODO set up correctly payment (how much person can get, and - for money of user)
@dp.message_handler(state=GetMoney.Finish)
async def finish_check(message: types.Message, state: FSMContext):
    await GetMoney.next()
    if message.text in get_all_locales("да"):
        async with state.proxy() as data:
            try:
                res = payeer.transfer(data['amount'], data["wallet_code"], "RUB", "RUB", comment=str(message.chat.id))
            except PayeerAPIException as error:
                if str(repr(error)) == "PayeerAPIException(['transferHimselfForbidden'])":
                    await message.answer(_("Напишите правильные данные и попробуйте заново"), reply_markup=main_keyboard())
                else:
                    await message.answer(_("Произошла ошибка. Попробуйте снова немного позже"), reply_markup=main_keyboard())
                    for id_a in admins:
                        await bot.send_message(id_a, _("Произошла ошибка в боте @{}. Описание: {}").
                                               format(BOT_ALIAS, str(repr(error))))
                return
            await Transaction(paying_sys_id=200, user_id=message.chat.id, rub_amount=data['amount'],
                              bot_pay=True, wallet_number=data["wallet_code"]).save()  # code 200 means it's from bot
            user = await User.get_or_none(user_id=message.chat.id)
            await User.filter(user_id=message.chat.id).update(income=(float(user.income) - float(data['amount'])))
            config = await User.get(user_id=1000)
            await User.filter(user_id=1000).update(income=(config.income + float(data['amount'])))
            await message.answer(_("Оплата завершена. спасибо что используете нашего бота!"),
                                 reply_markup=main_keyboard())
    else:
        await message.answer(_("Напишите \"да\" чтобы подтвердить или /cancel чтобы отменить или переписать данные"))
