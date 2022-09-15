from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import CommandStart

from models.role import UserRole
from services.database import Database
from filters.chat import PrivateChat


async def admin_start(message: Message, data: Database):
    await data.get_users()
    await message.reply("Hello, admin!")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(
        admin_start, CommandStart(), PrivateChat(), state="*", role=UserRole.ADMIN,
    )
