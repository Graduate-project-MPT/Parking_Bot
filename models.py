from sqlalchemy import create_engine, Column, Integer, Boolean, \
                       String, Text, BigInteger, ForeignKey, \
                       TIMESTAMP, select, desc, BooleanClauseList
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

from datetime import timedelta, datetime
from aiogram.types import Message
from typing import Optional
from config import settings
import random


Base = declarative_base()
engine = create_engine(
    settings.CON_STRING,
    echo=True,
    connect_args={'user': 'root', 'password': 'root'})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, expire_on_commit=False)
session = Session()

# Константы
TELEGRAM_ID = "telegram_id"
MESSAGE_ID = "message_id"

# Класс пользователя
class WPUser(Base):
    __tablename__ = 'wp_user'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    user_login = Column(String(255), nullable=False, unique=True)
    user_pass = Column(String(255), nullable=False)
    user_nicename = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=False)
    user_url = Column(String(255), nullable=False)
    user_registered = Column(TIMESTAMP, nullable=False)
    user_status = Column(Integer, nullable=False)
    user_display_name = Column(String(255), nullable=False)

    usermeta = relationship('WPUserMeta', back_populates='user')

# Класс мета данных пользователя
class WPUserMeta(Base):
    __tablename__ = 'wp_usermeta'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    user_meta_key = Column(String(100), nullable=True)
    user_meta_value = Column(Text, nullable=True)

    user_id = Column(BigInteger,
                     ForeignKey('wp_user.ID'), nullable=False)

    user = relationship('WPUser', back_populates='usermeta')

# Класс сообщений
class WPMessage(Base):
    __tablename__ = 'wp_message'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    message_date = Column(BigInteger, nullable=False)
    message_user_telegram_id = Column(BigInteger, nullable=False)
    message_bot_telegram_id = Column(BigInteger, nullable=False)
    message_telegram_id = Column(BigInteger, nullable=False)
    message_text = Column(Text, nullable=True)

    message_answer_id = Column(BigInteger,
                               ForeignKey('wp_message.ID'), nullable=True)
    user_id = Column(BigInteger,
                     ForeignKey('wp_user.ID'), nullable=True)

# Класс документов
class WPDocument(Base):
    __tablename__ = 'wp_document'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    document_file_id = Column(String(100), nullable=True)
    document_file_unique_id = Column(String(100), nullable=True)
    document_file_size = Column(BigInteger, nullable=False)
    document_file_url = Column(Text, nullable=True)
    document_file_mime = Column(Text, nullable=True)

    message_id = Column(BigInteger,
                        ForeignKey('wp_message.ID'), nullable=False)

# Класс парковочных мест
class WPPlace(Base):
    __tablename__ = 'wp_place'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    place_is_valid = Column(Boolean, nullable=False, default=1)
    place_code = Column(String(4), nullable=False)

    reserve = relationship('WPReserve', back_populates='place')

# Класс резервации парковочных мест
class WPReserve(Base):

    __tablename__ = 'wp_reserve'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    reserve_begin = Column(BigInteger, nullable=False)
    reserve_end = Column(BigInteger, nullable=True)
    reserve_is_deleted = Column(Boolean, nullable=False, default=0)

    place_id = Column(BigInteger,
                      ForeignKey('wp_place.ID'), nullable=True)
    user_id = Column(Boolean,
                     ForeignKey('wp_user.ID'), nullable=False)

    place = relationship('WPPlace', back_populates='reserve')


# Редактирование данных
# Добавляет запись в БД
def sql_add(data):
    try:
        session.add(data)
        session.commit()
        session.close()
        return True
    except Exception as e:
        print("\n\nsql_add\n", e, "\n\n\n")
        return False

# Удаляет запись бд
def sql_delete(data):
    try:
        session.delete(data)
        session.commit()
        session.close()
    except Exception as e:
        print("\n\sql_delete\n", e, "\n\n\n")

def sql_query(class_example, filter_condition: BooleanClauseList):
    try:
        query_result = session.query(class_example).filter(filter_condition)
        session.close()
        return (query_result)
    except Exception as e:
        print("\n\sql_query\n", e, "\n\n\n")
        return None

# Запросы
# Возвращает запись пользователя по его логину
def find_user_by_login(login: str) -> WPUser | None:
    return sql_query(WPUser, (WPUser.user_login == login)).first()

# Возвращает парковочное место по его наименованию
def find_places_by_code(place_code: list[str]) -> list[WPPlace] | None:
    filter_condition = (WPPlace.place_code.in_(place_code))
    return sql_query(WPPlace, filter_condition).all()

# Возвращает мета запись телеграм кода
def find_usermeta_by_telegram_id(telegram_id: int) -> WPUserMeta | None:
    filter_condition = (WPUserMeta.user_meta_value == telegram_id) & \
                        (WPUserMeta.user_meta_key == TELEGRAM_ID)
    return sql_query(WPUserMeta, filter_condition).first()

# Возвращает запись пользователя авторизированного под данным кодом телеграма
def find_user_by_telegram_id(telegram_id: int) -> WPUser | None:
    meta = find_usermeta_by_telegram_id(telegram_id)
    if meta:
        print("\n\nmeta id = ", meta.ID, "\n\n")
        user = sql_query(WPUser, (WPUser.ID == meta.user_id)).first()
        print("\n\nuser id = ")
        return user
    print("\n\nmeta id = NONE\n\n")
    return None

# Возвращает актуальные резервации по телеграм коду авторизированного подльзователя
def find_actual_reserves(user: WPUser, is_deleted: bool = False) -> list[WPReserve] | None:
    actual_timestamp = datetime.now().timestamp()
    filter_condition = (WPReserve.user_id == user.ID) & \
                        (WPReserve.reserve_end > actual_timestamp) & \
                        (WPReserve.reserve_is_deleted == is_deleted)
    return sql_query(WPReserve, filter_condition).all()

# Возвращает все резервации по телеграм коду авторизированного подльзователя
def find_reserves(user: WPUser, is_deleted: bool = False) -> list[WPReserve] | None:
    filter_condition = (WPReserve.user_id == user.ID) & \
                        (WPReserve.reserve_is_deleted == is_deleted)
    return sql_query(WPReserve, filter_condition).all()

# Возвращает место по его коду
def find_place_by_id(place_id: int) -> WPPlace | None:
    filter_condition = (WPPlace.ID == place_id)
    return sql_query(WPPlace, filter_condition).first()

# Возвращение записи сообщении по его коду сообщени телеграма
def find_message_by_id(message_id: int, is_bot: bool = True) -> WPMessage | None:
    if is_bot:
        filter_condition = (WPMessage.message_telegram_id == message_id) & (~WPMessage.user_id)
    else:
        filter_condition = (WPMessage.message_telegram_id == message_id) & (WPMessage.user_id)
    return sql_query(WPMessage, filter_condition).first()

# Находит запись сообщение по коду сообщения отправленного ботом
def find_bot_message_by_id(message_bot_id: int, is_bot: bool = True) -> WPMessage | None:
    if is_bot:
        filter_condition = (WPMessage.message_bot_telegram_id == message_bot_id) & (WPMessage.user_id == None)
    else:
        filter_condition = (WPMessage.message_bot_telegram_id == message_bot_id) & (WPMessage.user_id != None)
    mess = sql_query(WPMessage, filter_condition).first()
    return mess

# Находит запись сообщение по коду сообщения отправленного пользователем
def find_message_by_user_id(user_id: int) -> WPMessage | None:
    filter_condition = (WPMessage.user_id == user_id)
    return sql_query(WPMessage, filter_condition).order_by(desc(WPMessage.ID)).first()

#
def find_user_message_id(user_id: int) -> WPUserMeta | None:
    return sql_query(WPUserMeta, (WPUserMeta.user_id == user_id)).first()

# Проерка авторизирован ли пользователь под данным телеграм кодом
def is_telegram_id_set(user: WPUser, telegram_id: int) -> WPUserMeta | None:
    filter_condition = (WPUserMeta.user_id == user.ID) & (WPUserMeta.user_meta_key == TELEGRAM_ID)
    return sql_query(WPUserMeta, filter_condition).first()


# Запросы изменений
# Создание резервации места на парковке (Если вернет False резервация не удалась)
def add_reserves(user: WPUser, hours_count: int) -> WPPlace | None:
    now = datetime.now()
    timestamp_begin = now.timestamp()
    timestamp_end = (now + timedelta(hours=hours_count)).timestamp()
    filter_condition_reserve = (WPReserve.reserve_begin.between(timestamp_begin, timestamp_end)) | \
                       (WPReserve.reserve_end.between(timestamp_begin, timestamp_end))
    reserves = sql_query(WPReserve, filter_condition_reserve)
    if reserves.count() > 0:
        filter_condition_place = (~WPPlace.ID.in_([x.place_id for x in reserves.all()]))
    else:
        filter_condition_place = (True)
    place: WPPlace | None = random.choice(sql_query(WPPlace, filter_condition_place).all())
        
    if not place:
        return None

    new_reserve = WPReserve(
        reserve_begin=timestamp_begin,
        reserve_end=timestamp_end,
        place_id=place.ID,
        user_id=user.ID,
    )
    if sql_add(new_reserve):
        return place

# Удаление резервации
def delete_reserves(user: WPUser, places: list[WPPlace]):
    filter_condition = (WPReserve.reserve_end > datetime.now().timestamp()) & \
                       (WPReserve.user_id == user.ID) & \
                       (WPReserve.place_id.in_([place.ID for place in places])) & \
                       (~WPReserve.reserve_is_deleted)
    reserves = sql_query(WPReserve, filter_condition)

    if reserves:
        reserves.update({
            'reserve_is_deleted': True
        })
        session.commit()
        session.close()
        return True
    return False

# Сохранение телеграм кода пользователя как авторизированного
def save_telegram_id(user: WPUser, telegram_id: int) -> None:
    filter_condition = (WPUserMeta.user_id == user.ID) & \
                       (WPUserMeta.user_meta_key == TELEGRAM_ID)
    usermeta = sql_query(WPUserMeta, filter_condition).first()

    if usermeta:
        usermeta.user_meta_value = telegram_id
    else:
        usermeta = WPUserMeta(user_id=user.ID,
                              user_meta_key=TELEGRAM_ID,
                              user_meta_value=telegram_id)
        session.add(usermeta)
    session.commit()
    session.close()

# Сохранение сообщения в базе данных
def save_message(my_message: Message, formated_text: str, bot_message: Message, user_id: int | None, answer_id: Optional[int]) -> WPMessage | None:
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

def save_file(file: WPDocument) -> None:
    sql_add(file)
