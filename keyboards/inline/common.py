from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.classes import WPUser, WPPlace, WPReserve

class ButtonIK:
    RESERVE_DELL = "Отменить бронирование"
    RESERVE_LIST = "Просмотр одобренных бронированний"
    RESERVE_DATA = "Просмотр бронирований"

class ReserveIDHandler(CallbackData, prefix='place_callback'):
    reserve_id: int

def build_reserve_action(reserve: WPReserve):
    builder = InlineKeyboardBuilder()
    reserve_id_handler = ReserveIDHandler(reserve.ID)
    builder.button(
        text=ButtonIK.RESERVE_DELL,
        callback_data=reserve_id_handler.pack(),
    )
    InlineKeyboardMarkup(

    )
    return builder.as_markup(resize_keyboard=True)
