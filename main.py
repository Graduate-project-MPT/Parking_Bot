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
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)
    # await settings.bot.delete_message(from_user_id, msg_id.message_id)

if __name__ == "__main__":
    asyncio.run(main())

# from models import find_bot_message_by_id, sql_query, WPMessage

# print("\n\nID = ", sql_query(WPMessage, ((WPMessage.message_bot_telegram_id == 1100) & (WPMessage.user_id == None))).first().ID, "\n\n")

# mess = find_bot_message_by_id(1100)

# if mess:
#     print("\n\nTest ID = ", mess.ID, "\n\n")
# else:
#     print("\n\nTest ID = NULL\n\n")
    