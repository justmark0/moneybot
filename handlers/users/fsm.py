from handlers.users.messages import get_all_locales
from aiogram.dispatcher import FSMContext
from payeer_api import PayeerAPIException
from keyboards.default.keyboards import *
from keyboards.inline.keyboards import *
from loader import dp, _, payeer, bot
from aiogram.types import ParseMode
from states.states import *
from data.models import *
from data.config import *
import requests
import hashlib
import json
import re


async def notify_admins_about_error(message, system, error_text):
    await message.answer(_("Произошла ошибка. Попробуйте снова немного позже"),
                         reply_markup=main_keyboard())
    for id_a in admins:
        await bot.send_message(id_a, _("#error\nПроизошла ошибка в боте @{}. Система {}.Описание: {}").
                               format(BOT_ALIAS, system, error_text))


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
        await message.answer(_("Вы можете пополнить счет несколькими способами:"), reply_markup=pay_options())
        await state.finish()
    elif message.text in get_all_locales("Снять деньги 💰"):
        await message.answer(_("Вы можете вывести деньги несколькими способами:"), reply_markup=get_money())

        await state.finish()
        await GetMoney.next()
    else:
        await message.answer(_("Используйте клавиатуру чтобы выбрать возможные опции"))


@dp.message_handler(state=GetMoney.System)
async def select_amount(message: types.message, state: FSMContext):
    if message.text in ["Fkwallet", "Payeer"]:
        async with state.proxy() as data:
            data['system'] = message.text.lower()
        user = await User.get_or_none(user_id=message.chat.id)
        await message.answer(_("Минимальная сумма вывода {min_out} рублей\nВы можете вывести {money} рублей.\nВведите "
                               "сумму которую хотите вывести:\n\n(можете исползовать /cancel чтобы выйти)").
                             format(min_out=MIN_MONEY_OUT, money=(user.income + user.money)),
                             reply_markup=types.ReplyKeyboardRemove())
        await GetMoney.next()
    else:
        await message.answer(_("Используйте клавиатуру чтобы выбрать возможные опции"))


@dp.message_handler(state=GetMoney.Amount)
async def select_amount(message: types.message, state: FSMContext):
    if re.fullmatch(r"[+-]?([0-9]*[.])?[0-9]+", message.text):
        user = await User.get_or_none(user_id=message.chat.id)
        if float(message.text) > user.money + user.income:
            await message.answer(_("Вы можете вывести только {money} рублей").format(money=(user.money + user.income)))
            return
        if float(message.text) < MIN_MONEY_OUT:
            await message.answer(_("Минимальная сумма которую можно вывести из бота {} рублей").format(MIN_MONEY_OUT))
            return
        async with state.proxy() as data:
            data['amount'] = float(message.text)
            await message.answer(_("Введите ваш номер вашего {sys} кошелька").format(sys=data['system']))
        await GetMoney.next()
    else:
        await message.answer(_("Вы можете использовать только цифры"))


@dp.message_handler(state=GetMoney.WalletNumber)
async def select_wallet(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if (re.fullmatch(r"P[a-zA-Z0-9]{7,12}", message.text) and data['system'] == "payeer") or \
                (re.fullmatch(r"F[0-9]{6,15}", message.text) and data['system'] == 'fkwallet'):
            data['wallet_code'] = message.text
            await message.answer(
                _("Вы уверены что хотите выслать {money} рублей на кошелек {wallet}?\n\nНапишите \"да\" "
                  "чтобы подтвердить.").format(money=data['amount'], wallet=message.text),
                reply_markup=confirm_keyboard())
            await GetMoney.next()
        else:
            await message.answer(_("Номер кошелька для Payeer начинается с P и содержит 7-12 цифр. Например P1000000\n"
                                   "Номера кошельков Fkwallet начинаются с F и содержат цифры. Например F100000000"))


@dp.message_handler(state=GetMoney.Finish)
async def finish_check(message: types.Message, state: FSMContext):
    await GetMoney.next()
    if message.text in get_all_locales("да"):
        async with state.proxy() as data:
            if data['system'] == "fkwallet":
                if data['wallet_code'] == FKWALLET_WALLET_CODE:
                    await message.answer(_("Напишите правильные данные и попробуйте заново"),
                                         reply_markup=main_keyboard())
                    return
                sign_str = FKWALLET_WALLET_CODE + str(data['amount']) + str(data['wallet_code']) + FKWALLET_API_KEY
                sign = hashlib.md5(sign_str.encode()).hexdigest()
                data_req = {"wallet_id": FKWALLET_WALLET_CODE, "purse": str(data['wallet_code']),
                        "amount": str(data['amount']), "sign": sign, "action": "transfer"}
                res_str = requests.post("https://www.fkwallet.ru/api_v1.php", data=data_req)
                res = json.loads(res_str.text)
                if "desc" not in res.keys():
                    await notify_admins_about_error(message, 'fkwallet', f"Responce starts with: "
                                                             f"{res_str.text[:max(len(res_str.text) - 1, 100):]}")
                    await message.answer(_("Произошла ошибка. Попробуйте снова немного позже"))
                    return
                if res['desc'] != "Payment send":
                    await notify_admins_about_error(message, 'fkwallet', f"Responce starts with: "
                                                             f"{res_str.text[:max(len(res_str.text) - 1, 100):]}")
                    await message.answer(_("Произошла ошибка. Попробуйте снова немного позже"))
                    return
            elif data['system'] == 'payeer':
                try:
                    res = payeer.transfer(data['amount'], data["wallet_code"], "RUB", "RUB",
                                          comment=str(message.chat.id))
                except PayeerAPIException as error:
                    if str(repr(error)) == "PayeerAPIException(['transferHimselfForbidden'])":
                        await message.answer(_("Напишите правильные данные и попробуйте заново"),
                                             reply_markup=main_keyboard())
                        return
                    else:
                        await notify_admins_about_error(message, 'payeer', str(repr(error)))
                        await message.answer(_("Произошла ошибка. Попробуйте снова немного позже"))
                        return
            await Transaction(paying_sys_id=200, user_id=message.chat.id, rub_amount=data['amount'],
                              bot_pay=True, system=data['system'], wallet_number=data['wallet_code']).save()
            # code 200 means it's from bot
            user = await User.get_or_none(user_id=message.chat.id)
            if user.income >= float(data['amount']):
                income = user.income - float(data['amount'])
                money = user.money
            else:
                income = 0
                amount = float(data['amount']) - user.income
                money = user.money - amount
            await User.filter(user_id=message.chat.id).update(income=income, money=money)
            config = await User.get(user_id=1000)
            await User.filter(user_id=1000).update(income=(config.income + float(data['amount'])))
            await message.answer(_("Оплата завершена!"),
                                 reply_markup=main_keyboard())
            await state.finish()
    else:
        await message.answer(_("Напишите \"да\" чтобы подтвердить или /cancel чтобы отменить или переписать данные"))


@dp.message_handler(state=PutMoney.Amount)
async def select_wallet(message: types.Message, state: FSMContext):
    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", message.text):
        exist = await CurrentTrans.get_or_none(amount=float(message.text))
        if exist is not None:
            await message.answer(_("Пожалуйста поменяйте сумму(можно на рубль). Или попробуйте снова через {t} минут").
                                 format(t=TTL_TRANSACTION))
            return
        async with state.proxy() as data:
            data['amount'] = message.text
            await message.answer(_("Вы хотите пополнить счет на {amount} рублей?").format(amount=data['amount']),
                                 reply_markup=confirm_keyboard())
            await PutMoney.next()
    else:
        await message.answer(_("Вводите только числа. Если хотите использовать нецелые числа пишите через точку"))


@dp.message_handler(state=PutMoney.Finish)
async def select_wallet(message: types.Message, state: FSMContext):
    if message.text in get_all_locales("да"):
        async with state.proxy() as data:
            amount = data['amount'].replace(".", "\.")
            await message.answer(
                _("💰*Для пополнения вашего баланса переведите {amount} рублей на кошелек Fkwallet:* `{"
                  "wallet}`\nПополняйте ТОЛЬКО *рублевым* счетом\. Пополните счет в течении {ttl} "
                  "минут\. Если вам не хватило этого времени можете снова написать боту сколько "
                  "хотите пополнить и пополнить в течении {ttl} минут\. При возникнивении проблем "
                  "пишите @VPankoff\.В течении минуты после пополнения ваш счет обновится\.\n"
                  "https://www\.fkwallet\.ru/ "
                  ).format(amount=amount, wallet=FKWALLET_WALLET_CODE, ttl=TTL_TRANSACTION),
                parse_mode=ParseMode.MARKDOWN_V2, reply_markup=main_keyboard())
            await CurrentTrans(user_id=message.chat.id, amount=float(data['amount'])).save()
            await PutMoney.next()
    else:
        await message.answer(_("Напишите \"да\" чтобы подтвердить или /cancel чтобы отменить или переписать данные"))


@dp.message_handler(state=SetPercent.Finish)
async def finish_check(message: types.Message, state: FSMContext):
    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", message.text):
        await User.filter(user_id=1001).update(money=1 + float(message.text))
        await message.answer("Готово", reply_markup=main_keyboard())
        await state.finish()
    else:
        await message.answer(_("Вводите только числа. Если хотите использовать нецелые числа пишите через точку"))