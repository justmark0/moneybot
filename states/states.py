from aiogram.dispatcher.filters.state import StatesGroup, State


class Language(StatesGroup):
    NewLanguage = State()


class Money(StatesGroup):
    PutGet = State()


class GetMoney(StatesGroup):
    System = State()
    Amount = State()
    WalletNumber = State()
    Finish = State()


class PutMoney(StatesGroup):
    Amount = State()
    Finish = State()


class SetPercent(StatesGroup):
    Finish = State()
