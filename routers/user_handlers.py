import bcrypt
from typing import Optional, List
from aiogram import Router, types
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ErrorEvent, BotCommand, MessageEntity, InputFile, BufferedInputFile
from filters.chat_type_filter import ChatTypeFilter

from config import settings

from models import WPReserve, \
    find_user_by_login, save_telegram_id, is_telegram_id_set, \
    find_user_by_telegram_id, find_actual_reserves, \
    find_reserves, find_place_by_id, remove_row, \
    add_reserves, delete_reserves, find_place_by_code
from main import bot

router = Router(name=__name__)

# Создание ответа с выводом списка резерваций
def get_reserves_list(reserves:Optional[List[WPReserve]]):
    if(not reserves):
        return "<b>Резервирований не найдено!</b>"
    line = "<h1>Список резерваций</h1>\n\n"
    for reserve in reserves:
        line += f"{reserve.place.place_code}: {reserve.reserve_begin} - {reserve.reserve_end}\n"
    return line

def is_user_authorized(telegram_id:int):
    return find_user_by_telegram_id(telegram_id)

# Запрос на автризацию
@router.message(Command(BotCommand(command="login", description="Авторизация")))
async def command_login_handler(message: Message) -> None:
    try:
        _, login, password = message.text.split(' ')
    except ValueError:
        await message.reply("Неверный формат команды. (Используйте: /login Логин Пароль)")
        return
    
    user = find_user_by_login(login)
    if not user:
        await message.reply("Пользователь с таким логином не существует.")
        return
    if is_telegram_id_set(user, message.from_user.id):
        await message.reply("Вы уже авторизованы на этом аккаунте.")
        return

    if user and bcrypt.checkpw(password.encode('utf-8'), user.user_pass.encode("utf-8")):
        save_telegram_id(user.ID, message.from_user.id)
        await message.reply("Вход выполнен успешно!")
        await bot.send_message(
            chat_id=settings.GROUP_ID,
            text=f"Пользователь {login} зашёл в аккаунт под телеграмм логином {message.from_user.username}"
        )
        meta = find_user_by_telegram_id(message.from_user.id)
        if meta and meta.user_meta_value != str(message.from_user.id):
            await bot.send_message(
                chat_id=meta.user_meta_value,
                text=f"В ваш аккаунт зашёл другой человек, вы больше не авторизованы. 🙂",
            )
            remove_row(meta)
    else:
        await message.reply("Неверный логин или пароль.")

# Запрос на выход из аккаунта
@router.message(Command(BotCommand(command="exit", description="Выход")))
async def command_login_handler(message: Message) -> None:
    user_meta = find_user_by_telegram_id(message.from_user.id)
    if(user_meta):
        remove_row(user_meta)
        await message.answer("Вы вышли из аккаунта!")
        return
    await message.answer("Вы не были авторизованны!")
    return
    
# Получение списка актуальных резерваций парковочных мест
@router.message(Command(BotCommand(command="reserve_list", description="Список резерваций")))
async def command_get_actual_reserves(message: Message) -> None:
    if(not is_user_authorized(message.from_user.id)):
        message.answer("<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML)
        return
    
    reserves = find_actual_reserves(message.from_user.id, message.date.timestamp())
    await message.answer(get_reserves_list(reserves),
        parse_mode=ParseMode.HTML)

# Получение списка всех резерваций парковочных мест
@router.message(Command(BotCommand(command="reserve_history", description="История резерваций")))
async def command_get_reserves(message: Message) -> None:
    if(not is_user_authorized(message.from_user.id)):
        message.answer("<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML)
        return
    
    reserves = find_reserves(message.from_user.id)
    await message.answer(get_reserves_list(reserves),
        parse_mode=ParseMode.HTML)

# Добавление новой резервации
@router.message(Command(BotCommand(command="reserve_add", description="Добавить резервацию")))
async def command_get_reserves(message: Message) -> None:
    if(not is_user_authorized(message.from_user.id)):
        message.answer("<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML)
        return
    
    try:
        _, hours_count = message.text.split(' ')
        hours_count = int(hours_count)
    except:
        await message.reply("Неверный формат команды. (Используйте: /reserve_add Количество_часов_резервации)")
        return
    place = add_reserves(find_user_by_telegram_id(message.from_user.id), hours_count)
    if place:
        await message.answer(f"Резервация прошла <b>успешно</b>\n \
                             Ваше парковочное место - {place.place_code}",
            parse_mode=ParseMode.HTML)
    else:
        await message.answer("<b>Резервация провалилась</b>",
            parse_mode=ParseMode.HTML)

# Удаление актуальной резервации
@router.message(Command(BotCommand(command="reserve_delete", description="Удаление резервацию")))
async def command_get_reserves(message: Message) -> None:
    if(not is_user_authorized(message.from_user.id)):
        message.answer("<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML)
        return
   
    try:
        _, place_code = message.text.split(' ')
    except:
        await message.reply("Неверный формат команды. (Используйте: /reserve_delete Код_парковочного_места)")
        return
    if delete_reserves(find_user_by_telegram_id(message.from_user.id), find_place_by_code(place_code)):
        await message.answer("<b>Резервация удалена</b>",
            parse_mode=ParseMode.HTML)
    else:
        await message.answer("<b>Удалить резервацию не удалось!</b>",
            parse_mode=ParseMode.HTML)
    
