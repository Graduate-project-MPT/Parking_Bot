from aiogram import Router, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message, BotCommand, ReplyKeyboardRemove
import bcrypt

from .base_func import is_authorize

from db.classes import WPUser
from db.queries.base import sql_delete
from db.queries.get import get_user_by_login, get_user_meta_exist, get_usermeta_by_telegram_id
from db.queries.post import save_telegram_id
from filters.chat_type_filter import ChatTypeFilter
from keyboards.reply.common import get_auth_rk, get_no_auth_rk, ButtonRK
from config import settings

router = Router(name=__name__)

# Помощь с коммандой авторизации
@router.message(F.text == ButtonRK.AUTH)
async def command_login_help(message: Message):
    await message.answer(
        "Для авторизации пропишите команду /login \"Логин\" \"Пароль\""
    )

# Запрос на автризацию
@router.message(Command(BotCommand(command="login", description="Авторизация")),
                ChatTypeFilter(chat_type=["private"]))
async def command_login_handler(message: Message):
    try:
        _, login, password = message.text.split(' ')
    except Exception as e:
        await message.reply(
            "Неверный формат команды. (Используйте: /login \"Логин\" \"Пароль\")",
            reply_markup=get_no_auth_rk()  
        )
        return

    user = get_user_by_login(login)
    if not user:
        await message.reply(
            "Пользователь с таким логином не существует.",
            reply_markup=get_no_auth_rk()  
        )
        return
    if get_user_meta_exist(user, message.from_user.id):
        await message.reply(
            "Вы уже авторизованы на этом аккаунте.",
            reply_markup=get_auth_rk()  
        )
        return

    if user and bcrypt.checkpw(password.encode('utf-8'), user.user_pass.encode("utf-8")):
        save_telegram_id(user, message.from_user.id)
        await message.reply(
            "Вход выполнен успешно!",
            reply_markup=get_auth_rk()  
        )
        await message.bot.send_message(
            chat_id=settings.GROUP_ID,
            text=f"Пользователь {login} зашёл в аккаунт под телеграмм логином {message.from_user.username}"
        )
        meta = get_usermeta_by_telegram_id(message.from_user.id)
        if meta and meta.user_meta_value != str(message.from_user.id):
            await message.bot.send_message(
                chat_id=meta.user_meta_value,
                text=f"В ваш аккаунт зашёл другой человек, "
                     f"вы больше не авторизованы. 🙂",
                reply_markup=get_no_auth_rk()
            )
            sql_delete(meta)
    else:
        await message.reply(
            "Неверный логин или пароль.",
            reply_markup=get_no_auth_rk()  
        )

# Запрос на выход из аккаунта
@router.message(F.text == ButtonRK.EXIT)
@router.message(Command(BotCommand(command="exit", description="Выход")),
                ChatTypeFilter(chat_type=["private"]))
async def command_login_handler(message: Message):
    user_meta = get_usermeta_by_telegram_id(message.from_user.id)
    if user_meta:
        sql_delete(user_meta)
        await message.answer(
            "Вы вышли из аккаунта!",
            reply_markup=get_no_auth_rk()  
        )
        return
    await message.answer(
        "Вы не были авторизованны!",
        reply_markup=get_no_auth_rk()  
    )
    return

# Запрос на получение логина аккаунта
@router.message(F.text == ButtonRK.LOGIN)
@router.message(Command(BotCommand(command="get_login", description="Получить логин")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_login_handler(message: Message):
    user:WPUser = is_authorize(message)
    if not user:
        return
    message.answer(
        "Ваш логин - <b>{user.user_login}</b>",
        parse_mode=ParseMode.HTML
    )
