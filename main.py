from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import settings
from routers import router as main_router
import asyncio
import logging


async def main():
    dp = Dispatcher()
    dp.include_router(main_router)
    bot = Bot(
        token=settings.TOKEN_API,
        parse_mode=ParseMode.HTML
    )
    file_log = logging.FileHandler('Log.log')
    console_out = logging.StreamHandler()

    logging.basicConfig(handlers=(file_log, console_out), 
                        format='[%(asctime)s | %(levelname)s]: %(message)s', 
                        datefmt='%m.%d.%Y %H:%M:%S',
                        level=logging.INFO)

    logging.info('Info message??))')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    