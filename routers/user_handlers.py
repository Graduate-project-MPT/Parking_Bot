from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message, BotCommand, BufferedInputFile
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
    find_message_by_id, save_user_message, find_message_by_user_id, \
    save_file, find_bot_message_by_id
from routers.commands.markup import get_auth_markup, get_no_auth_markup
from aiogram.types import ReplyKeyboardMarkup
import bcrypt
import io

router = Router(name=__name__)

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

def get_begin_message_id(message: Message):
    return 1


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
            reply_markup=get_no_auth_markup()  
        )
        return

    user = find_user_by_login(login)
    if not user:
        await message.reply(
            "Пользователь с таким логином не существует.",
            reply_markup=get_no_auth_markup()  
        )
        return
    if is_telegram_id_set(user, message.from_user.id):
        await message.reply(
            "Вы уже авторизованы на этом аккаунте.",
            reply_markup=get_auth_markup()  
        )
        return

    if user and bcrypt.checkpw(password.encode('utf-8'), user.user_pass.encode("utf-8")):
        save_telegram_id(user, message.from_user.id)
        await message.reply(
            "Вход выполнен успешно!",
            reply_markup=get_auth_markup()  
        )
        await settings.bot.send_message(
            chat_id=settings.GROUP_ID,
            text=f"Пользователь {login} зашёл в аккаунт под телеграмм логином {message.from_user.username}"
        )
        meta = find_usermeta_by_telegram_id(message.from_user.id)
        if meta and meta.user_meta_value != str(message.from_user.id):
            await settings.bot.send_message(
                chat_id=meta.user_meta_value,
                text=f"В ваш аккаунт зашёл другой человек, "
                     f"вы больше не авторизованы. 🙂",
                reply_markup=get_no_auth_markup()
            )
            sql_delete(meta)
    else:
        await message.reply(
            "Неверный логин или пароль.",
            reply_markup=get_no_auth_markup()  
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
            reply_markup=get_no_auth_markup()  
        )
        return
    await message.answer(
        "Вы не были авторизованны!",
        reply_markup=get_no_auth_markup()  
    )
    return


# Запросы на резервирование
# Получение списка актуальных резерваций парковочных мест
@router.message(Command(BotCommand(command="reserve_list", description="Список резерваций")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_actual_reserves(message: Message):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_markup()
        )
        return

    reserves = find_actual_reserves(user, False)
    await message.answer(
        get_reserves_list(reserves),
        parse_mode=ParseMode.HTML,
        reply_markup=get_auth_markup()
    )

# Получение списка всех резерваций парковочных мест
@router.message(Command(BotCommand(command="reserve_history", description="История резерваций")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_reserves(message: Message):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_markup()
        )
        return

    reserves = find_reserves(user)
    await message.answer(
        get_reserves_list(reserves),
        parse_mode=ParseMode.HTML,
        reply_markup=get_auth_markup()
    )

# Добавление новой резервации
@router.message(Command(BotCommand(command="reserve_add", description="Добавить резервацию")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_reserves(message: Message):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_markup()
        )
        return

    try:
        _, hours_count = message.text.split(' ')
        hours_count = int(hours_count)
    except Exception:
        await message.reply(
            "Неверный формат команды. (Используйте: /reserve_add Количество_часов_резервации)",
            reply_markup=get_auth_markup()
        )
        return
    place = add_reserves(user, hours_count)
    if place:
        await message.answer(
            f"Резервация прошла <b>успешно</b>\n    Ваше парковочное место - {place.place_code}",
            parse_mode=ParseMode.HTML,
            reply_markup=get_auth_markup()
        )
    else:
        await message.answer(
            "<b>Резервация провалилась</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_auth_markup()
        )

# Удаление актуальной резервации
@router.message(Command(BotCommand(command="reserves_delete", description="Удаление резервацию")),
                ChatTypeFilter(chat_type=["private"]))
async def command_get_reserves(message: Message):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_markup()
        )
        return

    try:
        places: list[str] = message.text.split(' ')
    except Exception:
        await message.reply(
            "Неверный формат команды. (Используйте: /reserve_delete Код_парковочного_места)",
            reply_markup=get_auth_markup()
        )
        return
    if delete_reserves(user, find_places_by_code(places)):
        await message.answer(
            "<b>Резервация удалена</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_auth_markup()
        )
    else:
        await message.answer(
            "<b>Удалить резервацию не удалось!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_auth_markup()
        )

async def send_mess(message: Message, user: WPUser):
    try:
        str_array = message.caption.split(' ')
        if(str_array[0] != "send_help"):
            return
        mess_test = ''.join(map(str.capitalize, str_array[1:]))
    except:
        return
    if message.reply_to_message:
        bot_mess = message.reply_to_message
        reply_data = find_bot_message_by_id(bot_mess.message_id)
        if reply_data:            
            bot_message = await settings.bot.send_message(
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
            return save_user_message(message, bot_message, user.ID, reply_data.ID)

    bot_message = await settings.bot.send_message(
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
    return save_user_message(message, bot_message, user.ID, answer_id=None)
# Запросы на техническую помощь
# Обработка сообщения
@router.message(F.photo, ChatTypeFilter(chat_type=["private"]))
async def photo_handler(message: types.Message, state: FSMContext):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_markup()
        )
        return

    photo = message.photo[-1]
    file_in_io = io.BytesIO()
    file = await settings.bot.get_file(photo.file_id)
    await settings.bot.download_file(file.file_path, destination=file_in_io)

    file_bytes = file_in_io.read(photo.file_size)

    if message.caption is not None:
        bot_message = await settings.bot.send_message(
            chat_id=settings.GROUP_ID,
            text=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                 f"От: `{user.user_nicename}`\n"
                 f"email: `{user.user_email}`\n\n"
                 f"Текст сообщения:\n"
                 f"{message.caption}",
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
        save_user_message(message, bot_message, user, answer_id=None)

    message_db = find_message_by_user_id(user.ID)
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

@router.message(F.document, ChatTypeFilter(chat_type=["private"]))
async def document_handler(message: types.Message):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_markup()
        )
        return

    message_db = None #send_mess(message=message, user=user)
    if message.caption:
        if message.reply_to_message:
            bot_mess = message.reply_to_message
            reply_data = find_bot_message_by_id(bot_mess.message_id)
            if reply_data:            
                bot_message = await settings.bot.send_message(
                    chat_id=settings.GROUP_ID,
                    reply_to_message_id=reply_data.message_telegram_id,
                    text=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                            f"От: `{user.user_nicename}`\n"
                            f"email: `{user.user_email}`\n\n"
                            f"Текст сообщения:\n"
                            f"{message.text}",
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
                message_db = save_user_message(message, bot_message, user.ID, reply_data.ID)
        else:
            bot_message = await settings.bot.send_message(
                chat_id=settings.GROUP_ID,
                text=f"[Данные пользователя:]"
                    f"(https://t.me/{message.from_user.username})\n"
                    f"От: `{user.user_nicename}`\n"
                    f"email: `{user.user_email}`\n\n"
                    f"Текст сообщения:\n"
                    f"{message.text}",
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
            message_db = save_user_message(message, bot_message, user.ID, answer_id=None)


        bot_message = await settings.bot.send_message(
            chat_id=settings.GROUP_ID,
            text=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
                 f"От: `{user.user_nicename}`\n"
                 f"email: `{user.user_email}`\n\n"
                 f"Текст сообщения:\n"
                 f"{mess_test}",
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        message_db = save_user_message(message, bot_message, user.ID, answer_id=None)
    else:
        message_db = find_message_by_user_id(user.ID)

    if not message_db:
        document = message.document
        file = await settings.bot.get_file(document.file_id)
        file_in_io = io.BytesIO()
        await settings.bot.download_file(file.file_path, destination=file_in_io)

        file_bytes = file_in_io.read(document.file_size)
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
            caption=f"[Данные пользователя:]"
                    f"(https://t.me/{message.from_user.username})\n"
                    f"От: `{user.user_nicename}`\n"
                    f"email: `{user.user_email}`\n\n",
            parse_mode=ParseMode.MARKDOWN_V2,
            document=BufferedInputFile(file_bytes, filename=document.file_name),
        )

@router.message(ChatTypeFilter(chat_type=["private"]))
async def private_message(message: Message):
    user = find_user_by_telegram_id(message.from_user.id)
    if not user:
        message.answer(
            "<b>Вы не авторизированны!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_no_auth_markup()
        )
        return

    send_mess(message=message, user=user)

    # if message.reply_to_message:
    #     bot_mess = message.reply_to_message
    #     reply_data = find_bot_message_by_id(bot_mess.message_id)
    #     if reply_data:            
    #         bot_message = await settings.bot.send_message(
    #             chat_id=settings.GROUP_ID,
    #             reply_to_message_id=reply_data.message_telegram_id,
    #             text=f"[Данные пользователя:](https://t.me/{message.from_user.username})\n"
    #                     f"От: `{user.user_nicename}`\n"
    #                     f"email: `{user.user_email}`\n\n"
    #                     f"Текст сообщения:\n"
    #                     f"{message.text}",
    #             parse_mode=ParseMode.MARKDOWN_V2,
    #             disable_web_page_preview=True
    #         )
    #         save_user_message(message, bot_message, user.ID, reply_data.ID)
    #         return

    # bot_message = await settings.bot.send_message(
    #     chat_id=settings.GROUP_ID,
    #     text=f"[Данные пользователя:]"
    #          f"(https://t.me/{message.from_user.username})\n"
    #          f"От: `{user.user_nicename}`\n"
    #          f"email: `{user.user_email}`\n\n"
    #          f"Текст сообщения:\n"
    #          f"{message.text}",
    #     parse_mode=ParseMode.MARKDOWN_V2,
    #     disable_web_page_preview=True
    # )
    # save_user_message(message, bot_message, user.ID, answer_id=None)
