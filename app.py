from tortoise import Tortoise
from data.config import DB_URL
from data.models import User


async def on_startup(dp):
    import middlewares
    middlewares.setup(dp)
    await Tortoise.init(db_url=DB_URL, modules={"models": ["data.models"]})
    await User.get_or_create(user_id=1000, language="en")

if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
