from aiogram import Router
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message, BotCommand

from .base_func import is_authorize, get_reserves_list

from db.classes import WPUser
from db.queries.get import get_actual_reserve, get_reserves, get_places_by_code
from db.queries.post import add_reserves, delete_reserves 
from keyboards.reply.common import get_auth_rk, get_no_auth_rk
from keyboards.inline.common import build_reserve_action
from filters.chat_type_filter import ChatTypeFilter
from config import settings

router = Router(name=__name__)

# Получение списка актуальных резерваций парковочных мест
@router.message(Command(BotCommand(command="reserve", description="Мои бронирования")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_actual_reserves(message: Message):
    user: WPUser = await is_authorize(message)
    if not user:
        return

    reserves = get_actual_reserve(user)
    await message.answer(
        get_reserves_list(reserves),
        parse_mode=ParseMode.HTML,
        reply_markup=get_auth_rk()
    )

# Получение списка всех резерваций парковочных мест
@router.message(Command(BotCommand(command="reserve_history", description="История бронированний")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_reserves(message: Message):
    user: WPUser = await is_authorize(message)
    if not user:
        return

    reserves = get_reserves(user)
    await message.answer(
        get_reserves_list(reserves),
        parse_mode=ParseMode.HTML,
        reply_markup=get_auth_rk()
    )

# Добавление новой резервации
@router.message(Command(BotCommand(command="reserve_add", description="Забронировать место")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_reserves(message: Message):
    user: WPUser = await is_authorize(message)
    if not user:
        return

    try:
        _, hours_count = message.text.split(' ')
        hours_count = int(hours_count)
    except Exception:
        await message.reply(
            "Неверный формат команды. (Используйте: /reserve_add Количество_часов_резервации)",
            reply_markup=get_auth_rk()
        )
        return
    place = add_reserves(user, hours_count)
    if place:
        await message.answer(
            f"Резервация прошла <b>успешно</b>\n    Ваше парковочное место - {place.place_code}",
            parse_mode=ParseMode.HTML,
            reply_markup=build_reserve_action(reserve_id=place.place_code),
        )
    else:
        await message.answer(
            "<b>Резервация провалилась</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_auth_rk()
        )

# Удаление актуальной резервации
@router.message(Command(BotCommand(command="reserve_delete", description="Удаленить бронь")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_reserves(message: Message):
    user: WPUser = await is_authorize(message)
    if not user:
        return

    try:
        places: list[str] = message.text.split(' ')
    except Exception:
        await message.reply(
            "Неверный формат команды. (Используйте: /reserve_delete Код_парковочного_места)",
            reply_markup=get_auth_rk()
        )
        return
    if delete_reserves(user, get_places_by_code(places)):
        await message.answer(
            "<b>Резервация удалена</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_auth_rk()
        )
    else:
        await message.answer(
            "<b>Удалить резервацию не удалось!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_auth_rk()
        )
