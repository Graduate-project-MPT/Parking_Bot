import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher

from aiogram.enums import ParseMode

from config import settings
from routers import router as main_router

bot = Bot(
    token=settings.TOKEN_API,
    parse_mode=ParseMode.HTML,
)

async def main():
    dp = Dispatcher()
    dp.include_router(main_router)

    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())