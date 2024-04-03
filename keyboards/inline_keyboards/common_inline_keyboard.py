from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

class ButtonIK:
    RESERVE_DELL = "Отменить бронирование"
    RESERVE_LIST = "Просмотр одобренных бронированний"
    RESERVE_DATA = "Просмотр бронирований"

class ReserveIDHandler(CallbackData, prefix="id-handler"):
    ID: int

def get_added_reserve_ik(reserve_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    reserve_id_handler = ReserveIDHandler(reserve_id)
    builder.button(
        text=ButtonIK.ButtonIK,
        callback_data=reserve_id_handler.pack(),
    )
    return builder.as_markup()
