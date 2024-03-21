from aiogram import Router, types, F
from aiogram.enums import ChatAction
from filters.chat_type_filter import ChatTypeFilter

router = Router(name=__name__)

@router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def secret_admin_message(message: types.Message):
    await message.reply("Hi, group!")