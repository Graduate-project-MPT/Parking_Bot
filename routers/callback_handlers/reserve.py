from keyboards.inline.reserve import ReserveAction, ReserveBotCallback, ReserveUserCallback  
from aiogram.types import CallbackQuery
from aiogram import Router, F

from db.queries.get import get_places_by_code
from db.queries.post import delete_reserve_by_id, add_place_to_reserve_by_id
from config import settings

# from models import 

router = Router(name=__name__)

@router.callback_query(ReserveBotCallback.filter(F.action == ReserveAction.delete))
async def delete_bot_reserve(
    callback_query: CallbackQuery,
    callback_data: ReserveBotCallback
):
    if delete_reserve_by_id(callback_data.reserve_id):
        await callback_query.bot.edit_message_reply_markup(
            message_id=callback_data.user_message_id,
            chat_id=callback_data.chat_telegram_id,
            reply_markup=None,
        )
        await callback_query.bot.send_message(
            text="<b>Заявка была отклонена!</b>",
            reply_to_message_id=callback_data.user_message_id,
            chat_id=callback_data.chat_telegram_id
        )
        await callback_query.message.delete()
    await callback_query.answer()

@router.callback_query(ReserveBotCallback.filter(F.action == ReserveAction.approve))
async def approve_bot_reserve(
    callback_query: CallbackQuery,
    callback_data: ReserveBotCallback
):
    place = add_place_to_reserve_by_id(callback_data.reserve_id)
    if place:
        await callback_query.message.delete()
        await callback_query.bot.send_message(
            text=f"Ваша заявка была была принита <b>парковочное место = {place.place_code}</b>",
            reply_to_message_id=callback_data.user_message_id,
            chat_id=callback_data.chat_telegram_id
        )
    await callback_query.answer()

@router.callback_query(ReserveUserCallback.filter())
async def delete_user_reserve(
    callback_query: CallbackQuery,
    callback_data: ReserveUserCallback
):
    if delete_reserve_by_id(callback_data.reserve_id):
        await callback_query.message.edit_reply_markup(
            reply_markup=None
        )
        await callback_query.bot.delete_message(
            chat_id=settings.RESERVETION_GROUP_ID,
            message_id=callback_data.bot_message_id
        )
    await callback_query.answer(f"")
