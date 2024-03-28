from re import Match

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import BotCommand
from filters.chat_type_filter import ChatTypeFilter

from config import settings

router = Router(name=__name__)


@router.message(Command(BotCommand(command="Users", description="Получить пользователей")),
                ChatTypeFilter(chat_type=["private"]),
                F.from_user.id == settings.ADMIN_ID)
async def secret_admin_message(message: types.Message):
    await message.reply("Hi, admin!")