from loader import dp, _
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


@dp.message_handler()
async def bot_echo(message: types.Message):
    config_user = await User.get(user_id=1000)
    if message.text in get_all_locales("Пополнить или снять деньги 💳"):
        await message.answer(_("Выберите что хотите сделать"), reply_markup=put_get_money())
        await Money.next()
    elif message.text in get_all_locales("Инфо 📈"):
        days = (datetime.now(timezone.utc) - config_user.reg_date).days + int(WORKING_FOR)
        people = len(list(await User.exclude(is_blocked=True)))
        await message.answer(_("Всем доброго времени суток. Я Влад @VPankoff уже 5 год занимаюсь трейдом на крипте, "
                               "спб и мск бирже. Я и мой друг решили помочь заработать тебе вкусить жить успешного "
                               "трейдера. Всем кто хочет научиться трейдить переходи на канал моего друга {}, "
                               "а если тебе и так хорошо получай процент от своих вложений, которые мы "
                               "приумножим.\n🔸Бот работает уже  {} дней\n🔸Вот выплатил уже {} "
                               "рублей\n🔸Зарегестрированно уже {} человек").
                             format(CHANNEL_NAME, days, float(SENT_MONEY) + config_user.income, people + int(PEOPLE)))

    elif message.text in get_all_locales("Мой аккаунт 💼"):
        user = await User.get_or_none(user_id=message.chat.id)
        if user is None:
            await message.answer(_("Вы не зарегестрированны, используйте /start"))
            return

        user_upd = await User.get_or_none(user_id=message.chat.id)
        days = datetime.now(timezone.utc) - user_upd.reg_date  # Subtracting dates to know for how long user using bot
        await message.answer(_("Ваш аккаунт 🔐\n"
                               "🔹У вас {money} руб. на счету.\n"
                               "🔹Вы можете вывести {take} рублей\n"
                               "🔹Вы пользуетесь {date} дней нашим ботом!\n"
                               "🔹Завтра у вас будет {tomorrow} руб.\n"
                               "🔹В настоящее время депозит состовляет {coef} % в день\n"
                               "🔹Вы можете посмотреть вашу историю транзакций с помощью /transactions").format(
            money=float(user_upd.money) + float(user_upd.income), take=float(user_upd.income),
            date=days.days, tomorrow=(float(user_upd.money) + float(user_upd.income)) * DEPOSIT_COEFFICIENT,
            coef=round((DEPOSIT_COEFFICIENT - 1) * 100, 1)), reply_markup=main_keyboard())

    elif message.text in get_all_locales("🇷🇺 Язык"):
        await message.answer(_("Какой язык хотите использовать?"), reply_markup=language_keyboard())
        await Language.next()
    else:
        await message.answer(_("Привет! Я помогу тебе заработать деньги!"), reply_markup=main_keyboard())
