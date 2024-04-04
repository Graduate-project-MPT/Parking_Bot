from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils import markdown

from db.queries.get import get_usermeta_by_telegram_id
from keyboards.reply.common import get_auth_rk, get_no_auth_rk
from filters.chat_type_filter import ChatTypeFilter

router = Router(name=__name__)

@router.message(CommandStart(), ChatTypeFilter(chat_type=["private"]))
async def handle_start(message: types.Message):
    
    markup:ReplyKeyboardMarkup
    if get_usermeta_by_telegram_id(message.from_user.id):
        markup = get_auth_rk()
    else:
        markup = get_no_auth_rk()
    await message.answer(
        f"Привет, {markdown.hbold(message.from_user.full_name)}!",
        parse_mode=ParseMode.HTML, reply_markup=markup
    )

@router.message(Command("help"), ChatTypeFilter(chat_type=["private"]))
async def handle_help(message: types.Message):
    markup:ReplyKeyboardMarkup
    if get_usermeta_by_telegram_id(message.from_user.id):
        markup = get_auth_rk()
    else:
        markup = get_no_auth_rk()
    await message.answer(
        "I am parking bot",
        parse_mode=ParseMode.HTML, reply_markup=markup
    )