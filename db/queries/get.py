from sqlalchemy import desc
from ..classes import TELEGRAM_ID, \
    WPMessage, WPPlace, WPReserve, WPUser, WPUserMeta
from .base import sql_query
from datetime import datetime

def get_reserve_by_id(ID: int):
    filter_condition = (WPReserve.ID == ID)
    return sql_query(WPReserve, filter_condition).first()

def get_user_by_login(login: str):
    return sql_query(WPUser, (WPUser.user_login == login)).first()

# Возвращает мета запись телеграм кода
def get_usermeta_by_telegram_id(telegram_id: int):
    filter_condition = (WPUserMeta.user_meta_value == telegram_id) & \
                        (WPUserMeta.user_meta_key == TELEGRAM_ID)
    return sql_query(WPUserMeta, filter_condition).first()

# Возвращает запись пользователя авторизированного под данным кодом телеграма
def get_user_by_telegram_id(telegram_id: int):
    meta = get_usermeta_by_telegram_id(telegram_id)
    if meta:
        user = sql_query(WPUser, (WPUser.ID == meta.user_id)).first()
        return user
    return None

# Находит запись сообщение по коду сообщения отправленного пользователем
def get_user_message(user_id: int):
    filter_condition = (WPMessage.user_id == user_id)
    return sql_query(WPMessage, filter_condition).order_by(desc(WPMessage.ID)).first()

def get_places_by_code(place_code: str):
    filter_condition = (WPPlace.place_code == place_code)
    return sql_query(WPPlace, filter_condition).first()

# Возвращает актуальные резервации по телеграм коду авторизированного подльзователя
def get_actual_reserve(user: WPUser):
    actual_timestamp = datetime.now().timestamp()
    filter_condition = (WPReserve.user_id == user.ID) & \
                       (WPReserve.reserve_end > actual_timestamp) & \
                       (~WPReserve.reserve_is_deleted) & \
                       (WPReserve.place_id)
    return sql_query(WPReserve, filter_condition).all()

# Возвращает актуальные резервации по телеграм коду авторизированного подльзователя
def get_reserve_request(user: WPUser):
    actual_timestamp = datetime.now().timestamp()
    filter_condition = (WPReserve.user_id == user.ID) & \
                       (WPReserve.reserve_end > actual_timestamp) & \
                       (~WPReserve.reserve_is_deleted)
    return sql_query(WPReserve, filter_condition).all()

# Возвращает все резервации по телеграм коду авторизированного подльзователя
def get_reserves(user: WPUser, is_deleted: bool = False):
    filter_condition = (WPReserve.user_id == user.ID) & \
                        (WPReserve.reserve_is_deleted == is_deleted)
    return sql_query(WPReserve, filter_condition).all()

# Находит запись сообщение по коду сообщения отправленного ботом
def get_bot_message_by_id(message_bot_id: int, is_bot: bool = True):
    if is_bot:
        filter_condition = (WPMessage.message_bot_telegram_id == message_bot_id) & (WPMessage.user_id == None)
    else:
        filter_condition = (WPMessage.message_bot_telegram_id == message_bot_id) & (WPMessage.user_id != None)
    mess = sql_query(WPMessage, filter_condition).first()
    return mess

# Находит запись сообщение по коду сообщения отправленного пользователем
def get_user_message(user_id: int):
    filter_condition = (WPMessage.user_id == user_id)
    return sql_query(WPMessage, filter_condition).order_by(desc(WPMessage.ID)).first()

# Проерка авторизирован ли пользователь под данным телеграм кодом
def get_user_meta_exist(user: WPUser, telegram_id: int):
    filter_condition = (WPUserMeta.user_meta_key == TELEGRAM_ID) & (WPUserMeta.user_meta_value == f"{telegram_id}")
    return sql_query(WPUserMeta, filter_condition).first()
