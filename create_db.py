from tortoise import Tortoise, run_async
from data.config import DB_URL


async def create():
    await Tortoise.init(db_url=DB_URL, modules={"models": ["data.models"]})
    await Tortoise.generate_schemas()

if __name__ == '__main__':
    run_async(create())
