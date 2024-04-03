import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CON_STRING: str = os.getenv('CON_STRING')
    GROUP_ID: str = os.getenv('GROUP_ID')
    ADMIN_ID: int = int(os.getenv('ADMIN_ID'))
    TOKEN_API: str = os.getenv('TOKEN_API')

settings = Settings()
