import os
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.enums import ParseMode


load_dotenv()


class Settings:
    CON_STRING: str = os.getenv('CON_STRING')
    GROUP_ID: str = os.getenv('GROUP_ID')
    ADMIN_ID: int = int(os.getenv('ADMIN_ID'))
    TOKEN_API: str = os.getenv('TOKEN_API')
    DEV_TOKEN_API: str = os.getenv('DEV_TOKEN_API')

    bot = Bot(
        token=TOKEN_API,
        parse_mode=ParseMode.HTML
    )


settings = Settings()
