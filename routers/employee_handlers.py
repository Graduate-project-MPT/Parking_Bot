from aiogram import Router, types, F
from aiogram.enums import ChatAction
import re
from filters.chat_type_filter import ChatTypeFilter
from aiogram.enums import ChatAction, ParseMode

from models import WPReserve, WPDocument, \
    find_user_by_login, save_telegram_id, is_telegram_id_set, \
    find_user_by_telegram_id, find_usermeta_by_telegram_id, find_actual_reserves, \
    find_reserves, remove_row, \
    add_reserves, delete_reserves, find_place_by_code, \
    find_message_by_id, save_user_message, find_bot_message_by_id, find_message_by_user_id, \
    save_file

from config import settings

router = Router(name=__name__)

# @router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
# async def secret_admin_message(message: types.Message):
#     await message.reply("Hi, group!")

@router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def group_message(message: types.Message) -> None:
    try:
        if message.reply_to_message:
            bot_mess = message.reply_to_message
            print("\n\n\n1\n\n\n")
            replied_message = find_bot_message_by_id(bot_mess.message_id, False)
            if replied_message:
                print("\n\n\n2\n\n\n")
                bot_message = await settings.bot.send_message(
                    chat_id=replied_message.message_user_telegram_id,
                    reply_to_message_id=replied_message.message_telegram_id,
                    text=f"{message.text}",
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
                save_user_message(message, bot_message, None, replied_message.message_telegram_id)
                return
    except Exception as e:
        print(e)
        await message.answer(f"Nice try!")