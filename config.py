import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self,
                 TOKEN_API:str,
                 GROUP_ID:str,
                 ADMIN_ID:list):
        self.TOKEN_API = TOKEN_API
        self.GROUP_ID = GROUP_ID
        self.ADMIN_ID = ADMIN_ID
    TOKEN_API: str
    GROUP_ID: str
    ADMIN_ID: list

settings = Settings(os.getenv('TOKEN_API'),
                    os.getenv('GROUP_ID'),
                    os.getenv('ADMIN_ID'))