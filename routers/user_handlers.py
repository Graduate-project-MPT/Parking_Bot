from aiogram import Router, types
from aiogram.enums import ChatAction
from filters.chat_type_filter import ChatTypeFilter

router = Router(name=__name__)

@router.message(ChatTypeFilter(chat_type=["private"]))
async def secret_admin_message(message: types.Message):
    await message.reply("Hi, user!")