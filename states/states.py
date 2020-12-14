from aiogram.dispatcher.filters.state import StatesGroup, State


class Language(StatesGroup):
    NewLanguage = State()


class Money(StatesGroup):
    PutGet = State()


class GetMoney(StatesGroup):
    Amount = State()
    WalletNumber = State()
    Finish = State()
