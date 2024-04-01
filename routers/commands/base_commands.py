from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils import markdown
from filters.chat_type_filter import ChatTypeFilter
from routers.commands.markup import get_auth_markup, get_no_auth_markup
from models import find_usermeta_by_telegram_id

router = Router(name=__name__)

@router.message(CommandStart(), ChatTypeFilter(chat_type=["private"]))
async def handle_start(message: types.Message):
    markup:ReplyKeyboardMarkup
    if find_usermeta_by_telegram_id(message.from_user.id):
        markup = get_auth_markup()
    else:
        markup = get_no_auth_markup()
    await message.answer(
        f"Привет, {markdown.hbold(message.from_user.full_name)}!",
        parse_mode=ParseMode.HTML, reply_markup=markup
    )

@router.message(Command("help"), ChatTypeFilter(chat_type=["private"]))
async def handle_help(message: types.Message):
    markup:ReplyKeyboardMarkup
    if find_usermeta_by_telegram_id(message.from_user.id):
        markup = get_auth_markup()
    else:
        markup = get_no_auth_markup()
    await message.answer(
        "I am parking bot",
        parse_mode=ParseMode.HTML, reply_markup=markup
    )