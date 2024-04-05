from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enum import IntEnum, auto

from db.classes import WPUser, WPPlace, WPReserve

class ButtonIK:
    RESERVE_DELL = "Отменить бронирование"
    RESERVE_APPROVE = "Одобрить бронирование"
    RESERVE_LIST = "Просмотр одобренных бронированний"
    RESERVE_DATA = "Просмотр бронирований"

class ReserveAction(IntEnum):
    delete = auto()
    approve = auto()

class ReserveBotCallback(CallbackData, prefix='reserve_bot_callback'):
    action: ReserveAction
    reserve_id: int
    user_message_id: int
    user_telegram_id: int

class ReserveUserCallback(CallbackData, prefix='reserve_user_callback'):
    reserve_id: int
    bot_message_id: int

def build_bot_reserve_action(reserve_id: int, message: Message):
    builder = InlineKeyboardBuilder()
    delete_reserve_handler = ReserveBotCallback(
        action=ReserveAction.delete, 
        reserve_id=reserve_id,
        user_message_id=message.message_id,
        user_telegram_id=message.from_user.id
    )
    approve_reserve_handler = ReserveBotCallback(
        action=ReserveAction.approve,
        reserve_id=reserve_id,
        user_message_id=message.message_id,
        user_telegram_id=message.from_user.id
    )
    builder.button(
        text=ButtonIK.RESERVE_DELL,
        callback_data=delete_reserve_handler.pack(),
    )
    builder.button(
        text=ButtonIK.RESERVE_APPROVE,
        callback_data=approve_reserve_handler.pack(),
    )
    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)

def build_user_reserve_action(reserve_id: int, message: Message):
    builder = InlineKeyboardBuilder()
    delete_reserve_handler = ReserveUserCallback(reserve_id=reserve_id, bot_message_id=message.message_id)
    builder.button(
        text=ButtonIK.RESERVE_DELL,
        callback_data=delete_reserve_handler.pack(),
    )
    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)
