from re import Match

from aiogram import Router, F, types
from magic_filter import RegexpMode
from filters.chat_type_filter import ChatTypeFilter

from config import settings

router = Router(name=__name__)


@router.message(ChatTypeFilter(chat_type=["private"]),
                F.from_user.id.in_(settings.ADMIN_ID))
async def secret_admin_message(message: types.Message):
    await message.reply("Hi, admin!")