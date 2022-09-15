import asyncio
import logging
import asyncpg

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage

from config import load_config
from filters.role import RoleFilter, AdminFilter
from filters.chat import PrivateChat, PublicChat
from handlers.admin import register_admin
from handlers.user import register_user
from middlewares.db import DbMiddleware
from middlewares.role import RoleMiddleware
from middlewares.throttling import ThrottlingMiddleware
from services.commands import set_default_commands

logger = logging.getLogger(__name__)


async def create_pool(user, password, database, host, echo):
    pool = await asyncpg.create_pool(
            user=user,
            password=password,
            host=host,
            port='5432',
            database=database
        )
    return pool


async def main():
    fmt_str = "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
    fmt_date_str = "%d.%m.%Y %H:%M:%S"
    logging.basicConfig(format=fmt_str, datefmt=fmt_date_str)
    logging.basicConfig(
        level=logging.INFO,
        format=fmt_str,
        datefmt=fmt_date_str
    )
    logger.error("Starting bot")
    config = load_config("bot.ini")

    if config.tg_bot.use_redis:
        storage = RedisStorage()
    else:
        storage = MemoryStorage()
    pool = await create_pool(
        user=config.db.user,
        password=config.db.password,
        database=config.db.database,
        host=config.db.host,
        echo=False,
    )

    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(DbMiddleware(pool))
    dp.middleware.setup(RoleMiddleware(config.tg_bot.admin_id))
    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(PrivateChat)
    dp.filters_factory.bind(PublicChat)

    register_admin(dp)
    register_user(dp)

    try:
        await set_default_commands(dp)
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


def start():
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")


if __name__ == '__main__':
    start()
