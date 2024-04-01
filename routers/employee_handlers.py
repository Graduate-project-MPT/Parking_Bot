from aiogram import Router, types, F
from aiogram.enums import ChatAction
import re
from filters.chat_type_filter import ChatTypeFilter
from aiogram.enums import ChatAction, ParseMode
from models import save_user_message, find_bot_message_by_id
from config import settings

router = Router(name=__name__)

@router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def group_message(message: types.Message) -> None:
    try:
        if message.reply_to_message:
            bot_mess = message.reply_to_message
            replied_message = find_bot_message_by_id(
                bot_mess.message_id,
                False
            )
            if replied_message:
                bot_message = await settings.bot.send_message(
                    chat_id=replied_message.message_user_telegram_id,
                    reply_to_message_id=replied_message.message_telegram_id,
                    text=f"{message.text}",
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
                save_user_message(
                    message,
                    bot_message,
                    None,
                    replied_message.ID
                )
                return
    except Exception:
        await message.answer(f"Nice try!")
