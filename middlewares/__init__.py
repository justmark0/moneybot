from aiogram import Dispatcher

from .throttling import ThrottlingMiddleware
from .language_middleware import ACLMiddleware
from data.config import I18N_DOMAIN, LOCALES_DIR


def setup(dp: Dispatcher):
    i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    dp.middleware.setup(ThrottlingMiddleware())
    return i18n
