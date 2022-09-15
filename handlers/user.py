from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.dispatcher.filters import CommandStart

from services.database import Database
from states.user import UserMain


async def user_start(message: Message, data: Database, state: FSMContext):
    await message.reply("Hello, user!")
    await state.set_state(UserMain.SOME_STATE)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, CommandStart(), state="*")
