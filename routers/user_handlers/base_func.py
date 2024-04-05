from aiogram.enums import ParseMode
from aiogram.types import Message
from typing import Optional, List
from datetime import datetime

from db.classes import WPReserve, WPUser
from db.queries.get import get_user_by_telegram_id, get_bot_message_by_id
from db.queries.post import add_message
from keyboards.reply.common import get_no_auth_rk, get_auth_rk
from config import settings

# Проверка авторизированности ползователя
async def is_authorize(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_rk()
        )
    return user

# Создание ответа с выводом списка резерваций
def get_reserves_list(reserves: Optional[List[WPReserve]]):
    if not reserves:
        return "<b>Резервирований не найдено!</b>"
    line = "<b>Список резерваций</b>\n\n"
    line += "<b>Парковочное место     Временной промежуток</b>\n"
    for reserve in reserves:
        date_begin = datetime.fromtimestamp(reserve.reserve_begin).strftime("%m/%d/%Y, %H:%M:%S")
        date_end = datetime.fromtimestamp(reserve.reserve_end).strftime("%m/%d/%Y, %H:%M:%S")
        line += f"                 <b>{reserve.place.place_code}</b>                {date_begin} / {date_end}\n"
    return line

# Отправка собщения пользователем
async def send_mess(message: Message, text_line: str, user: WPUser):
    try:
        str_array = text_line.split(' ')
        if(str_array[0] != "/send_help"):
            return None
        mess_test = ' '.join(map(str.capitalize, str_array[1:]))
    except Exception as e:
        await message.reply(
            "Неверный формат команды. (Используйте: /send_help текст)",
            reply_markup=get_auth_rk()  
        )
        return None
    if message.reply_to_message:
        bot_mess = message.reply_to_message
        reply_data = get_bot_message_by_id(bot_mess.message_id)
        if reply_data:            
            bot_message = await message.bot.send_message(
                chat_id=settings.GROUP_ID,
                reply_to_message_id=reply_data.message_telegram_id,
                text=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                        f"От: `{user.user_nicename}`\n"
                        f"email: `{user.user_email}`\n\n"
                        f"Текст сообщения:\n"
                        f"{mess_test}",
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
            return add_message(message, mess_test, bot_message, user.ID, reply_data.ID)

    bot_message = await message.bot.send_message(
        chat_id=settings.GROUP_ID,
        text=f"[Данные пользователя:]"
             f"(https://t.me/{message.from_user.username})\n"
             f"От: `{user.user_nicename}`\n"
             f"email: `{user.user_email}`\n\n"
             f"Текст сообщения:\n"
             f"{mess_test}",
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )
    return add_message(message, mess_test, bot_message, user.ID, answer_id=None)
