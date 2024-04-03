from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message, BotCommand, \
    BufferedInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from filters.chat_type_filter import ChatTypeFilter
from typing import Optional, List
from datetime import datetime
from config import settings
from models import WPReserve, WPDocument, WPUser, \
    find_user_by_login, save_telegram_id, is_telegram_id_set, \
    find_user_by_telegram_id, find_usermeta_by_telegram_id, \
    find_actual_reserves, find_reserves, sql_delete, \
    add_reserves, delete_reserves, find_places_by_code, \
    save_message, find_message_by_user_id, \
    save_file, find_bot_message_by_id
from keyboards.reply_keyboards.common_reply_keyboard import get_auth_rk, get_no_auth_rk
import bcrypt
import io

router = Router(name=__name__)

#region functions
# Отправка сообщения в группу сотрудников
async def send_mess(message: Message, text_line: str, user: WPUser):
    try:
        str_array = text_line.split(' ')
        if(str_array[0] != "/send_help"):
            return None
        mess_test = ' '.join(map(str.capitalize, str_array[1:]))
    except Exception as e:
        await message.reply(
            "Неверный формат команды. (Используйте: /send_help текст)",
            reply_markup=get_auth_rk()  
        )
        return None
    if message.reply_to_message:
        bot_mess = message.reply_to_message
        reply_data = find_bot_message_by_id(bot_mess.message_id)
        if reply_data:            
            bot_message = await message.bot.send_message(
                chat_id=settings.GROUP_ID,
                reply_to_message_id=reply_data.message_telegram_id,
                text=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                        f"От: `{user.user_nicename}`\n"
                        f"email: `{user.user_email}`\n\n"
                        f"Текст сообщения:\n"
                        f"{mess_test}",
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
            return save_message(message, mess_test, bot_message, user.ID, reply_data.ID)

    bot_message = await message.bot.send_message(
        chat_id=settings.GROUP_ID,
        text=f"[Данные пользователя:]"
             f"(https://t.me/{message.from_user.username})\n"
             f"От: `{user.user_nicename}`\n"
             f"email: `{user.user_email}`\n\n"
             f"Текст сообщения:\n"
             f"{mess_test}",
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )
    return save_message(message, mess_test, bot_message, user.ID, answer_id=None)

# Создание ответа с выводом списка резерваций
def get_reserves_list(reserves: Optional[List[WPReserve]]):
    if not reserves:
        return "<b>Резервирований не найдено!</b>"
    line = "<b>Список резерваций</b>\n\n"
    line += "<b>Парковочное место     Временной промежуток</b>\n"
    for reserve in reserves:
        date_begin = datetime.fromtimestamp(reserve.reserve_begin).strftime("%m/%d/%Y, %H:%M:%S")
        date_end = datetime.fromtimestamp(reserve.reserve_end).strftime("%m/%d/%Y, %H:%M:%S")
        line += f"                 <b>{reserve.place.place_code}</b>                {date_begin} / {date_end}\n"
    return line

# Проверка авторизированности ползователя
async def is_authorize(message: Message):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_rk()
        )
    return user
#endregion

#region auth
# Запросы авторизации
# Запрос на автризацию
@router.message(Command(BotCommand(command="login", description="Авторизация")),
                ChatTypeFilter(chat_type=["private"]))
async def command_login_handler(message: Message):
    try:
        _, login, password = message.text.split(' ')
    except ValueError:
        await message.reply(
            "Неверный формат команды. (Используйте: /login Логин Пароль)",
            reply_markup=get_no_auth_rk()  
        )
        return

    user = find_user_by_login(login)
    if not user:
        await message.reply(
            "Пользователь с таким логином не существует.",
            reply_markup=get_no_auth_rk()  
        )
        return
    if is_telegram_id_set(user, message.from_user.id):
        await message.reply(
            "Вы уже авторизованы на этом аккаунте.",
            reply_markup=get_auth_rk()  
        )
        return

    if user and bcrypt.checkpw(password.encode('utf-8'), user.user_pass.encode("utf-8")):
        save_telegram_id(user, message.from_user.id)
        await message.reply(
            "Вход выполнен успешно!",
            reply_markup=get_auth_rk()  
        )
        await message.bot.send_message(
            chat_id=settings.GROUP_ID,
            text=f"Пользователь {login} зашёл в аккаунт под телеграмм логином {message.from_user.username}"
        )
        meta = find_usermeta_by_telegram_id(message.from_user.id)
        if meta and meta.user_meta_value != str(message.from_user.id):
            await message.bot.send_message(
                chat_id=meta.user_meta_value,
                text=f"В ваш аккаунт зашёл другой человек, "
                     f"вы больше не авторизованы. 🙂",
                reply_markup=get_no_auth_rk()
            )
            sql_delete(meta)
    else:
        await message.reply(
            "Неверный логин или пароль.",
            reply_markup=get_no_auth_rk()  
        )

# Запрос на выход из аккаунта
@router.message(Command(BotCommand(command="exit", description="Выход")),
                ChatTypeFilter(chat_type=["private"]))
async def command_login_handler(message: Message):
    user_meta = find_usermeta_by_telegram_id(message.from_user.id)
    if user_meta:
        sql_delete(user_meta)
        await message.answer(
            "Вы вышли из аккаунта!",
            reply_markup=ReplyKeyboardRemove(), 
        )
        return
    await message.answer(
        "Вы не были авторизованны!",
        reply_markup=get_no_auth_rk()  
    )
    return
#endregion

#region reserve
# Запросы на резервирование
# Получение списка актуальных резерваций парковочных мест
@router.message(Command(BotCommand(command="reserve_list", description="Список резерваций")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_actual_reserves(message: Message):
    user = is_authorize(message)
    if not user:
        return

    reserves = find_actual_reserves(user, False)
    await message.answer(
        get_reserves_list(reserves),
        parse_mode=ParseMode.HTML,
        reply_markup=get_auth_rk()
    )

# Получение списка всех резерваций парковочных мест
@router.message(Command(BotCommand(command="reserve_history", description="История резерваций")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_reserves(message: Message):
    user = is_authorize(message)
    if not user:
        return

    reserves = find_reserves(user)
    await message.answer(
        get_reserves_list(reserves),
        parse_mode=ParseMode.HTML,
        reply_markup=get_auth_rk()
    )

# Добавление новой резервации
@router.message(Command(BotCommand(command="reserve_add", description="Добавить резервацию")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_reserves(message: Message):
    user = is_authorize(message)
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
            reply_markup=get_auth_rk(),
        )
    else:
        await message.answer(
            "<b>Резервация провалилась</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_auth_rk()
        )

# Удаление актуальной резервации
@router.message(Command(BotCommand(command="reserves_delete", description="Удаление резервацию")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_reserves(message: Message):
    user = is_authorize(message)
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
    if delete_reserves(user, find_places_by_code(places)):
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
#endregion

#region send help
# Запросы на техническую помощь
# Обработка сообщения
@router.message(F.photo, ChatTypeFilter(chat_type=["private"]))
async def command_send_photo_handler(message: types.Message, state: FSMContext):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_rk()
        )
        return

    message_db = None 
    if message.caption:
        message_db = await send_mess(message, message.caption, user)
    else:
        message_db = find_message_by_user_id(user.ID)

    if message_db:
        photo = message.photo[-1]
        file_in_io = io.BytesIO()
        file = await message.bot.get_file(photo.file_id)
        await message.bot.download_file(file.file_path, destination=file_in_io)

        file_bytes = file_in_io.read(photo.file_size)

        wp_document = WPDocument(
            message_id=message_db.ID,
            document_file_id=photo.file_id,
            document_file_unique_id=photo.file_unique_id,
            document_file_size=photo.file_size,
            document_file_url=f"https://api.telegram.org/file/"
                              f"bot{settings.TOKEN_API}/"
                              f"{file.file_path}",
            document_file_mime='photo',
        )
        save_file(wp_document)
        await message.bot.send_photo(
            chat_id=settings.GROUP_ID,
            reply_to_message_id=message_db.message_bot_telegram_id,
            caption=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                    f"От: `{user.user_nicename}`\n"
                    f"email: `{user.user_email}`\n\n",
            parse_mode=ParseMode.MARKDOWN_V2,
            photo=BufferedInputFile(file_bytes, filename=photo.file_unique_id)
        )

        await state.update_data(photo_0=photo, photo_counter=0)

        await state.set_state('next_photo')

@router.message(F.document, ChatTypeFilter(chat_type=["private"]))
async def command_send_document_handler(message: types.Message):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_rk()
        )
        return

    message_db = None 
    if message.caption:
        message_db = await send_mess(message, message.caption, user)
    else:
        message_db = find_message_by_user_id(user.ID)

    if message_db:
        document = message.document
        file = await message.bot.get_file(document.file_id)
        file_in_io = io.BytesIO()
        await message.bot.download_file(file.file_path, destination=file_in_io)

        file_bytes = file_in_io.read(document.file_size)
        wp_document = WPDocument(
            message_id=message_db.ID,
            document_file_id=document.file_id,
            document_file_unique_id=document.file_unique_id,
            document_file_size=document.file_size,
            document_file_url=f"https://api.telegram.org/file/"
                              f"bot{settings.TOKEN_API}/"
                              f"{file.file_path}",
            document_file_mime='document',
        )
        save_file(wp_document)

        await message.bot.send_document(
            chat_id=settings.GROUP_ID,
            reply_to_message_id=message_db.message_bot_telegram_id,
            caption=f"[Данные пользователя:]"
                    f"(https://t.me/{message.from_user.username})\n"
                    f"От: `{user.user_nicename}`\n"
                    f"email: `{user.user_email}`\n\n",
            parse_mode=ParseMode.MARKDOWN_V2,
            document=BufferedInputFile(file_bytes, filename=document.file_name),
        )

@router.message(Command(BotCommand(command="send_help", description="Обратиться к тех поддержке")),
                ChatTypeFilter(chat_type=["private"]))
async def command_send_help(message: Message):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_rk()
        )
        return
    
    await send_mess(message, message.text, user)
#endregion
