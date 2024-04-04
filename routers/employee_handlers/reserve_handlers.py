from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
from aiogram.enums import ParseMode

from db.queries.get import get_bot_message_by_id
from db.queries.post import add_message
from db.classes import WPUser
from filters.chat_type_filter import ChatTypeFilter
from keyboards.reply.common import get_auth_rk, get_no_auth_rk
from keyboards.inline.common import build_reserve_action
from filters.chat_type_filter import ChatTypeFilter

router = Router(name=__name__)

@router.message(Command(BotCommand(command="get_reserve", description="Получить логин")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_login_handler(message: Message):
    try:
        _, login = message.text.split(' ')
    except ValueError:
        await message.reply(
            "Неверный формат команды. (Используйте: /get_reserve Логин)",
            reply_markup=get_no_auth_rk()  
        )
        return
    # user:WPUser = get_user_by_login(message)
    # if not user:
    #     return
    # message.answer(
    #     "Ваш логин - <b>{user.user_login}</b>",
    #     parse_mode=ParseMode.HTML
    # )
