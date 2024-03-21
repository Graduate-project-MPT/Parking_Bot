import os
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ErrorEvent, BotCommand, MessageEntity, InputFile, BufferedInputFile
from aiogram.utils.markdown import hbold

from dotenv import load_dotenv

import logging

load_dotenv()

TOKEN_API = os.getenv('TOKEN_API')

bot = Bot(token=TOKEN_API)

group_id = os.getenv('GROUP_ID')

dp = Dispatcher()

router = Router()

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(
        f"Привет, {hbold(message.from_user.full_name)}!",
        parse_mode=ParseMode.HTML)

@dp.message(Command("help"))
async def handler_help(message: types.Message):
    await message.answer("I am parking bot")
    
@dp.message(Command("login"))
async def handler_login(message: types.Message):
    return;

@dp.message(Command("add_reserve"))
async def handler_login(message: types.Message):
    return;

@dp.message(Command("get_reserve"))
async def handler_login(message: types.Message):
    return;

@dp.message(Command("delete_reserve"))
async def handler_login(message: types.Message):
    return;

@dp.message()
async def handler_resend(message: types.Message):
    if message.text:
        await message.reply(
            text=message.text,
            entities=message.entities,
            parse_mode=None
        )
    else:
        try:
            await message.send_copy(chat_id=message.chat.id)
        except TypeError:
            await message.answer("Error")

async def start():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)