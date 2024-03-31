from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.utils import markdown


router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: types.Message):
    await message.answer(
        f"Привет, {markdown.hbold(message.from_user.full_name)}!",
        parse_mode=ParseMode.HTML)


@router.message(Command("help"))
async def handle_help(message: types.Message):
    await message.answer("I am parking bot")
