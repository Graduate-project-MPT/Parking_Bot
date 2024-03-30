import bcrypt
import io
from typing import Optional, List
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ErrorEvent, BotCommand, MessageEntity, InputFile, BufferedInputFile
from filters.chat_type_filter import ChatTypeFilter

from config import settings
from datetime import datetime
from models import WPReserve, WPDocument, \
    find_user_by_login, save_telegram_id, is_telegram_id_set, \
    find_user_by_telegram_id, find_usermeta_by_telegram_id, find_actual_reserves, \
    find_reserves, find_place_by_id, remove_row, \
    add_reserves, delete_reserves, find_place_by_code, \
    find_message_by_id, save_user_message, find_message_by_user_id, \
    save_file

router = Router(name=__name__)

# Создание ответа с выводом списка резерваций
def get_reserves_list(reserves:Optional[List[WPReserve]]):
    if(not reserves):
        return "<b>Резервирований не найдено!</b>"
    line = "<b>Список резерваций</b>\n\n"
    line += "<b>Парковочное место    Временной промежуток</b>\n"
    for reserve in reserves:
        line += f"                 <b>{reserve.place.place_code}</b>                    {datetime.fromtimestamp(reserve.reserve_begin)} - {datetime.fromtimestamp(reserve.reserve_end)}\n"
    return line

# Запросы авторизации
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
        save_telegram_id(user, message.from_user.id)
        await message.reply("Вход выполнен успешно!")
        await settings.bot.send_message(
            chat_id=settings.GROUP_ID,
            text=f"Пользователь {login} зашёл в аккаунт под телеграмм логином {message.from_user.username}"
        )
        meta = find_usermeta_by_telegram_id(message.from_user.id)
        if meta and meta.user_meta_value != str(message.from_user.id):
            await settings.bot.send_message(
                chat_id=meta.user_meta_value,
                text=f"В ваш аккаунт зашёл другой человек, вы больше не авторизованы. 🙂",
            )
            remove_row(meta)
    else:
        await message.reply("Неверный логин или пароль.")

# Запрос на выход из аккаунта
@router.message(Command(BotCommand(command="exit", description="Выход")))
async def command_login_handler(message: Message) -> None:
    user = find_user_by_telegram_id(message.from_user.id)
    if(user):
        remove_row(user)
        await message.answer("Вы вышли из аккаунта!")
        return
    await message.answer("Вы не были авторизованны!")
    return
    

# Запросы на резервирование
# Получение списка актуальных резерваций парковочных мест
@router.message(Command(BotCommand(command="reserve_list", description="Список резерваций")))
async def command_get_actual_reserves(message: Message) -> None:
    user = find_user_by_telegram_id(message.from_user.id)
    if(not user):
        message.answer("<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML)
        return
    
    reserves = find_actual_reserves(user.user, False)
    await message.answer(get_reserves_list(reserves),
        parse_mode=ParseMode.HTML)

# Получение списка всех резерваций парковочных мест
@router.message(Command(BotCommand(command="reserve_history", description="История резерваций")))
async def command_get_reserves(message: Message) -> None:
    user = find_user_by_telegram_id(message.from_user.id)
    if(not user):
        message.answer("<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML)
        return
    
    reserves = find_reserves(user.user)
    await message.answer(get_reserves_list(reserves),
        parse_mode=ParseMode.HTML)

# Добавление новой резервации
@router.message(Command(BotCommand(command="reserve_add", description="Добавить резервацию")))
async def command_get_reserves(message: Message) -> None:
    user = find_user_by_telegram_id(message.from_user.id)
    if(not user):
        message.answer("<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML)
        return
    
    try:
        _, hours_count = message.text.split(' ')
        hours_count = int(hours_count)
    except:
        await message.reply("Неверный формат команды. (Используйте: /reserve_add Количество_часов_резервации)")
        return
    place = add_reserves(user.user, hours_count)
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
    user = find_user_by_telegram_id(message.from_user.id)
    if(not user):
        message.answer("<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML)
        return
   
    try:
        _, place_code = message.text.split(' ')
    except:
        await message.reply("Неверный формат команды. (Используйте: /reserve_delete Код_парковочного_места)")
        return
    if delete_reserves(user.user, find_place_by_code(place_code)):
        await message.answer("<b>Резервация удалена</b>",
            parse_mode=ParseMode.HTML)
    else:
        await message.answer("<b>Удалить резервацию не удалось!</b>",
            parse_mode=ParseMode.HTML)
    

# Запросы на техническую помощь
# Обработка сообщения
@router.message(F.photo, ChatTypeFilter(chat_type=["private"]))
async def photo_handler(message: types.Message, state: FSMContext):
    try:
        user = find_user_by_telegram_id(message.from_user.id)
        if not user:
            message.answer("<b>Вы не авторизированны!</b>",
                parse_mode=ParseMode.HTML)
            return
        
        message_db = find_message_by_user_id(user.ID)

        photo = message.photo[-1]
        file_in_io = io.BytesIO()
        file = await settings.bot.get_file(photo.file_id)
        await settings.bot.download_file(file.file_path, destination=file_in_io)

        file_bytes = file_in_io.read(photo.file_size)

        if message.caption is not None:
            bot_message = await settings.bot.send_message(
                chat_id = settings.GROUP_ID,
                text=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                        f"От: `{user.user_nicename}`\n"
                        f"email: `{user.user_email}`\n\n"
                        "Текст сообщения:\n"
                        f"{message.caption}",
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
            save_user_message(message, bot_message, user, answer_id=None)

        if message_db is not None:
            wp_document = WPDocument(
                message_id=message_db.ID,
                document_file_id=photo.file_id,
                document_file_unique_id=photo.file_unique_id,
                document_file_size=photo.file_size,
                document_file_url=f"https://api.telegram.org/file/"
                                    f"bot{settings.DEV_TOKEN_API}/"
                                    f"{file.file_path}",
                document_file_mime='photo',
            )
            save_file(wp_document)
        await settings.bot.send_photo(
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
    except Exception as e:
        print("\n\n\nPhoto - ", e, "\n\n\n")
        await message.answer("Попробуйте снова")

@router.message(F.document, ChatTypeFilter(chat_type=["private"]))
async def document_handler(message: types.Message):
    try:
        user = find_user_by_telegram_id(message.from_user.id)
        if not user:
            message.answer("<b>Вы не авторизированны!</b>",
                parse_mode=ParseMode.HTML)
            return
        
        message_db = find_message_by_user_id(user.ID)

        document = message.document
        file_in_io = io.BytesIO()
        file = await settings.bot.get_file(document.file_id)
        await settings.bot.download_file(file.file_path, destination=file_in_io)

        file_bytes = file_in_io.read(document.file_size)

        if message.caption is not None:
            bot_message = await settings.bot.send_message(
                chat_id=settings.GROUP_ID,
                text=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                     f"От: `{user.user_nicename}`\n"
                     f"email: `{user.user_email}`\n\n"
                     "Текст сообщения:\n"
                     f"{message.caption}",
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            save_user_message(message, bot_message, user.ID, answer_id=None)

        if message_db is not None:
            wp_document = WPDocument(
                message_id=message_db.ID,
                document_file_id=document.file_id,
                document_file_unique_id=document.file_unique_id,
                document_file_size=document.file_size,
                document_file_url=f"https://api.telegram.org/file/"
                                  f"bot{settings.DEV_TOKEN_API}/"
                                  f"{file.file_path}",
                document_file_mime='document',
            )
            save_file(wp_document)

        await settings.bot.send_document(
            chat_id=settings.GROUP_ID,
            reply_to_message_id=message_db.message_bot_telegram_id,
            caption=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                    f"От: `{user.user_nicename}`\n"
                    f"email: `{user.user_email}`\n\n",
            parse_mode=ParseMode.MARKDOWN_V2,
            document=BufferedInputFile(file_bytes, filename=document.file_name),
        )
    except Exception as e:
        print("\n\n\Document - ", e, "\n\n\n")
        await message.answer("Попробуйте снова")

@router.message(ChatTypeFilter(chat_type=["private"]))
async def private_message(message: Message) -> None:
    try:
        user = find_user_by_telegram_id(message.from_user.id)
        if not user:
            message.answer("<b>Вы не авторизированны!</b>",
                parse_mode=ParseMode.HTML)
            return

        if message.reply_to_message:
            bot_mess = message.reply_to_message
            if bot_mess.from_user.full_name != "Parking Bot":
                replied_message_id = bot_mess.reply_to_message.message_id
                if find_message_by_id(replied_message_id, True):
                    bot_message = await settings.bot.send_message(
                        chat_id=settings.GROUP_ID,
                        reply_to_message_id=message.message_id,
                        text=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                                f"От: `{user.user_nicename}`\n"
                                f"email: `{user.user_email}`\n\n"
                                "Текст сообщения:\n"
                                f"{message.text}",
                        parse_mode=ParseMode.MARKDOWN_V2,
                        disable_web_page_preview=True
                    )
                    save_user_message(message, bot_message, user.ID, replied_message_id)
                    return

        bot_message = await settings.bot.send_message(
            chat_id=settings.GROUP_ID,
            text=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                    f"От: `{user.user_nicename}`\n"
                    f"email: `{user.user_email}`\n\n"
                    "Текст сообщения:\n"
                    f"{message.text}",
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
        save_user_message(message, bot_message, user.ID, answer_id=None)
    except Exception as e:
        print("\n\n\n text = ", e, "\n\n\n")
        await message.answer("Попробуйте снова")
