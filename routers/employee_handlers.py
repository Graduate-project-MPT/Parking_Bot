from aiogram import Router, types
from filters.chat_type_filter import ChatTypeFilter
from aiogram.enums import ParseMode
from models import save_message, find_bot_message_by_id
from config import settings

router = Router(name=__name__)

@router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def group_message(message: types.Message) -> None:
    if message.reply_to_message:
        bot_mess = message.reply_to_message
        replied_message = find_bot_message_by_id(bot_mess.message_id, False)
        if replied_message:            
            bot_message = await settings.bot.send_message(
                chat_id=replied_message.message_user_telegram_id,
                reply_to_message_id=replied_message.message_telegram_id,
                text=f"{message.text}",
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
            return save_message(message, message.text, bot_message, None, replied_message.ID)
