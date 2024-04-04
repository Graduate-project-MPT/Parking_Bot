from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

class ButtonIK:
    RESERVE_DELL = "Отменить бронирование"
    RESERVE_LIST = "Просмотр одобренных бронированний"
    RESERVE_DATA = "Просмотр бронирований"

class ReserveIDHandler(CallbackData, prefix='my_callback'):
    place_code: str

def build_reserve_action(place_code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    reserve_id_handler = ReserveIDHandler(place_code)
    builder.button(
        text=ButtonIK.ButtonIK,
        callback_data=reserve_id_handler.pack(),
    )
    return builder.as_markup()
