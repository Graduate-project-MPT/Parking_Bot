from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

class ButtonRK:
    AUTH = "Авторизация"
    SEND_HELP = "Техническая помощь"
    RESERVE_ADD = "Зарезервировать место"
    RESERVE_DELL = "Удалить резервацию"
    RESERVE_LIST = "Просмотр резерваций"
    RESERVE_HIS = "Просмотр истории резервированний"
    EXIT = "Выход из аккаунта"

def get_no_auth_rk():
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=ButtonRK.AUTH
    )
    return builder.as_markup()

def get_auth_rk():
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=ButtonRK.AUTH
    )
    builder.button(
        text=ButtonRK.RESERVE_ADD
    )
    builder.button(
        text=ButtonRK.RESERVE_DELL
    )
    builder.button(
        text=ButtonRK.RESERVE_LIST
    )
    builder.button(
        text=ButtonRK.RESERVE_HIS
    )
    builder.button(
        text=ButtonRK.EXIT
    )
    builder.adjust(1,2,2,1)
    return builder.as_markup()
