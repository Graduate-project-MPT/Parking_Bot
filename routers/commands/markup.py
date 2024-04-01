from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_no_auth_markup() -> ReplyKeyboardMarkup:
    kb = [
        [
            types.KeyboardButton(text="Авторизация")
        ],
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )

def get_auth_markup() -> ReplyKeyboardMarkup:
    sos_row = [
        KeyboardButton(text="Техническая помощь"),
    ]
    reserve_act_row = [ 
        KeyboardButton(text="Зарезервировать место"),
        KeyboardButton(text="Удалить резервацию"),
    ]
    reserve_row = [
        KeyboardButton(text="Просмотр резерваций"),
        KeyboardButton(text="Просмотр истории резервированний"),
    ]
    exit_row = [
        KeyboardButton(text="Выход из аккаунта")
    ]
    return ReplyKeyboardMarkup(
        keyboard=[sos_row, reserve_act_row, reserve_row, exit_row]
    )
