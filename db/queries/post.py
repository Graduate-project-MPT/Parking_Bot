from ..classes import session, TELEGRAM_ID, \
    WPDocument, WPMessage, WPPlace, WPReserve, WPUser, WPUserMeta
from .base import sql_add, sql_query, sql_commit
from aiogram.types import Message
from datetime import timedelta, datetime
import random

# Создание резервации места на парковке (Если вернет False резервация не удалась)
def add_reserves(user: WPUser, hours_count: int):
    now = datetime.now()
    timestamp_begin = now.timestamp()
    timestamp_end = (now + timedelta(hours=hours_count)).timestamp()

    new_reserve = WPReserve(
        reserve_begin=timestamp_begin,
        reserve_end=timestamp_end,
        reserve_is_deleted = False,
        reserve_is_started = False,
        place_id=None,
        user_id=user.ID,
    )
    if sql_add(new_reserve):
        return new_reserve
    
def add_place_to_reserve_by_id(reserve_id: int):
    filter_condition_reserve = (WPReserve.ID == reserve_id)
    reserve_query = sql_query(WPReserve, filter_condition_reserve)
    if not reserve_query.first():
        return None
    timestamp_begin = reserve_query.first().reserve_begin
    timestamp_end = reserve_query.first().reserve_end

    filter_condition_reserve = (
            (WPReserve.reserve_begin.between(timestamp_begin, timestamp_end)) | \
            (WPReserve.reserve_end.between(timestamp_begin, timestamp_end))
        ) & (WPReserve.place_id) & (~WPReserve.reserve_is_deleted)
    reserves = sql_query(WPReserve, filter_condition_reserve)
    if reserves.count() > 0:
        filter_condition_place = (~WPPlace.ID.in_([x.place_id for x in reserves.all()]))
    else:
        filter_condition_place = (True)
    place_list: list[WPPlace] = sql_query(WPPlace, filter_condition_place).all()
    place: WPPlace = random.choice(place_list)
        
    if not place:
        return None
    
    reserve_query.update({
        'place_id': place.ID
    })
    sql_commit()
    return place

# Удаление резервации
def delete_reserve_by_id(reserve_id: int):
    filter_condition = (WPReserve.ID == reserve_id)
    reserve = sql_query(WPReserve, filter_condition)

    if reserve:
        reserve.update({
            'reserve_is_deleted': True
        })
        return sql_commit()
    return False

# Удаление резервации
def delete_reserve(user: WPUser, place: WPPlace):
    filter_condition = (WPReserve.reserve_end > datetime.now().timestamp()) & \
                       (WPReserve.user_id == user.ID) & \
                       (WPReserve.place_id == place.ID) & \
                       (~WPReserve.reserve_is_deleted)
    reserves = sql_query(WPReserve, filter_condition)

    if reserves:
        reserves.update({
            'reserve_is_deleted': True
        })
        return sql_commit()
    return False

# Удаление резервации
def delete_reserve_ID(reserve_id: int):
    filter_condition = (~WPReserve.ID == reserve_id)
    reserves = sql_query(WPReserve, filter_condition)

    if reserves:
        reserves.update({
            'reserve_is_deleted': True
        })
        return sql_commit()
    return False

# Сохранение телеграм кода пользователя как авторизированного
def save_telegram_id(user: WPUser, telegram_id: int):
    filter_condition = (WPUserMeta.user_id == user.ID) & \
                       (WPUserMeta.user_meta_key == TELEGRAM_ID)
    usermeta_query = sql_query(WPUserMeta, filter_condition)

    if usermeta_query.first():
        usermeta_query.update({
            'user_meta_value': telegram_id
        })
        return sql_commit()
    else:
        usermeta = WPUserMeta(user_id=user.ID,
                              user_meta_key=TELEGRAM_ID,
                              user_meta_value=telegram_id)
        return sql_add(usermeta)

# Сохранение сообщения в базе данных
def add_message(my_message: Message, formated_text: str, bot_message: Message, user_id: int | None, answer_id: int | None):
    db_message = WPMessage(
        message_date=my_message.date.utcnow().timestamp(),
        message_user_telegram_id=my_message.from_user.id,
        message_bot_telegram_id=bot_message.message_id,
        message_telegram_id=my_message.message_id,
        message_text=formated_text,
        message_answer_id=answer_id,
        user_id=user_id
    )
    sql_add(db_message)

    return db_message

def add_document(file: WPDocument):
    sql_add(file)
