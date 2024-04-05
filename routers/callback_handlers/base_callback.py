from keyboards.inline.common import ReserveIDHandler
from aiogram.types import CallbackQuery
from aiogram import Router

from db.queries.get import get_places_by_code
from db.queries.post import delete_reserve

# from models import 

router = Router(name=__name__)

@router.callback_query(ReserveIDHandler.filter())
async def delete_reserve(
    callback_query: CallbackQuery,
    callback_data: ReserveIDHandler
):
    delete_reserve(callback_data.user, callback_data.place)
    await callback_query.message.answer(
        text=f"Press on button with place_code = {callback_data.place.place_code} and delete"
    )
    await callback_query.message.delete()
    return