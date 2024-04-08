from aiogram.utils.keyboard import ReplyKeyboardBuilder

class ButtonRK:
    AUTH = "Авторизация"
    LOGIN = "Получить свой логин"
    
    EXIT = "Выход из аккаунта"

def get_no_auth_rk():
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=ButtonRK.AUTH
    )
    return builder.as_markup(resize_keyboard=True)

def get_auth_rk():
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=ButtonRK.EXIT
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
