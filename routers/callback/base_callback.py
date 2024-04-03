from keyboards.inline_keyboards.common_inline_keyboard import ReserveIDHandler
from aiogram.types import CallbackQuery
from aiogram import Router

# from models import 

router = Router(name=__name__)

@router.callback_query(ReserveIDHandler.filter())
async def delete_reserve(
    callback_query: CallbackQuery,
    callback_data: ReserveIDHandler
):
    print("")