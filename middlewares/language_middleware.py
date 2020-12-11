from typing import Any, Tuple
from data.models import User
from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware


# TODO add get lang after database complete
async def get_lang(user_id):
    user = await User.get_or_none(user_id=user_id)
    if user is not None:
        return user.language


class ACLMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]):
        user = types.User.get_current()
        lang = await get_lang(user.id)
        if lang is None:
            return "en"
            # return user.locale[-2::].lower()
        return lang
