from aiogram import Dispatcher
from config import settings
from routers import router as main_router
import asyncio
import logging


async def main():
    dp = Dispatcher()
    dp.include_router(main_router)

    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(settings.bot)


if __name__ == "__main__":
    asyncio.run(main())
