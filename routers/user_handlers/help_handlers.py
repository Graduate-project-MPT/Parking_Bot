from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message, BotCommand, BufferedInputFile
from aiogram.fsm.context import FSMContext
import io

from .base_func import send_mess, is_authorize

from db.classes import WPDocument, WPUser
from db.queries.get import get_user_by_telegram_id, get_user_message
from db.queries.post import add_document 
from keyboards.reply.common import get_no_auth_rk
from filters.chat_type_filter import ChatTypeFilter
from config import settings

router = Router(name=__name__)

# Обработка сообщения
@router.message(F.photo, ChatTypeFilter(chat_type=["private"]))
async def command_send_photo_handler(message: types.Message, state: FSMContext):
    user: WPUser = await is_authorize(message)
    if not user:
        return

    message_db = None 
    if message.caption:
        message_db = await send_mess(message, message.caption, user)
    else:
        message_db = get_user_message(user.ID)

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
        add_document(wp_document)
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
    user: WPUser = await is_authorize(message)
    if not user:
        return

    message_db = None 
    if message.caption:
        message_db = await send_mess(message, message.caption, user)
    else:
        message_db = get_user_message(user.ID)

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
        add_document(wp_document)

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
    user: WPUser = await is_authorize(message)
    if not user:
        await message.answer("you not auth!")
        return
    
    await send_mess(message, message.text, user)