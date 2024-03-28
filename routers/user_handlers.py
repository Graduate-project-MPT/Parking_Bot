from aiogram import Router, types
from aiogram.enums import ChatAction
from filters.chat_type_filter import ChatTypeFilter

from config import settings

router = Router(name=__name__)

@router.message(ChatTypeFilter(chat_type=["private"]))
async def secret_admin_message(message: types.Message):
    await message.reply(f"Hi, user! {settings.ADMIN_ID}")