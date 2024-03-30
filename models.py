from sqlalchemy import create_engine, Column, Integer, Boolean, \
                       String, Text, BigInteger, ForeignKey, \
                       TIMESTAMP, not_, select, desc
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

from config import settings
from datetime import timedelta, datetime
from aiogram.types import Message
from typing import Optional

Base = declarative_base()
engine = create_engine(settings.CON_STRING, echo=True, connect_args={'user': 'root', 'password': 'root'})
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

    # Добавляем отношение usermeta
    usermeta = relationship('WPUserMeta', back_populates='user')

    # Добавляем отношение messages
    # messages = relationship('WPMessage', back_populates='user')

    # Добавляем отношение reserve
    # reserves = relationship('WPReserve', back_populates='user')
# Класс мета данных пользователя
class WPUserMeta(Base):
    __tablename__ = 'wp_usermeta'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('wp_user.ID'), nullable=False)
    user_meta_key = Column(String(100), nullable=True)
    user_meta_value = Column(Text, nullable=True)

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

    message_answer_id = Column(BigInteger, ForeignKey('wp_message.ID'), nullable=True)
    user_id = Column(BigInteger, ForeignKey('wp_user.ID'), nullable=True)
    # user = relationship('WPUser', back_populates='messages')
    # message_answer = relationship('WPMessage', remote_side=[ID])
    # document = relationship('WPDocument', back_populates='message')
# Класс документов
class WPDocument(Base):
    __tablename__ = 'wp_document'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, ForeignKey('wp_message.ID'), nullable=False)
    document_file_id = Column(String(100), nullable=True)
    document_file_unique_id = Column(String(100), nullable=True)
    document_file_size = Column(BigInteger, nullable=False)
    document_file_url = Column(Text, nullable=True)
    document_file_mime = Column(Text, nullable=True)

    # messagge = relationship('WPMessage', back_populates='document')
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
    
    place_id = Column(BigInteger, ForeignKey('wp_place.ID'), nullable=True)
    user_id = Column(Boolean, ForeignKey('wp_user.ID'), nullable=False)
    
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
def remove_row(data):
    session.delete(data)
    session.commit()

# Запросы
# Возвращает запись пользователя по его логину
def find_user_by_login(login:str):
    try:
        user = session.query(WPUser).filter(WPUser.user_login==login).first()
        session.close()
        return user
    except Exception as e:
        print(e)
        return None
# Возвращает парковочное место по его наименованию
def find_place_by_code(place_code:str):
    filter_condition =  (WPPlace.place_code == place_code)
    return session.query(WPPlace).filter(filter_condition).first()
# Возвращает мета запись телеграм кода
def find_usermeta_by_telegram_id(telegram_id:int):
    filter_condition =  (WPUserMeta.user_meta_value == telegram_id) & \
                        (WPUserMeta.user_meta_key == TELEGRAM_ID)
    return session.query(WPUserMeta).filter(filter_condition).first()
def find_user_by_telegram_id(telegram_id:int):
    meta = find_usermeta_by_telegram_id(telegram_id)
    if(not meta):
        return None
    return session.query(WPUser).filter(WPUser.ID == meta.user_id).first()
# Возвращает актуальные резервации по телеграм коду авторизированного подльзователя
def find_actual_reserves(user:WPUser, is_deleted:bool = False):
    try:
        actual_timestamp = datetime.now().timestamp();
        filter_condition =  (WPReserve.user_id == user.ID) & \
                            (WPReserve.reserve_end > actual_timestamp) & \
                            (WPReserve.reserve_is_deleted == is_deleted)
        return session.query(WPReserve).filter(filter_condition).all()
    except Exception as e:
        print("\n\nget_actual\n", e, "\n\n\n")
# Возвращает все резервации по телеграм коду авторизированного подльзователя
def find_reserves(user:WPUser, is_deleted:bool = False):
    filter_condition =  (WPReserve.user_id == user.ID) & \
                        (WPReserve.reserve_is_deleted == is_deleted)
    return session.query(WPReserve).filter(filter_condition).all()
# Возвращает место по его коду
def find_place_by_id(place_id:int, is_deleted:bool = False):
    filter_condition =  (WPPlace.ID==place_id)
    place = session.query(WPPlace).filter_by(filter_condition).first()
    session.close()
    return place
# Возвращение записи сообщении по его коду сообщени телеграма
def find_message_by_id(message_id:int, is_bot:bool):
    try:
        usermeta = session.query(WPMessage).filter(WPMessage.message_telegram_id == message_id)
        if is_bot:
            usermeta = usermeta.filter(WPMessage.user_id == None).first()
        else:
            usermeta = usermeta.filter(WPMessage.user_id != None).first()

        session.close()
        return usermeta
    except:
        return None
# 
def find_message_by_user_id(user_id: int):
    try:
        query = (
            select(WPMessage)
            .order_by(desc(WPMessage.ID))
            .where(WPMessage.user_id == user_id)
        )
        return session.scalars(query).first()
    except Exception as e:
        print(e)
        return None
# 
def find_user_message_id(user_id:int):
    return session.query(WPUserMeta).filter(WPUserMeta.user_id==user_id).first().user_message_id

# Проерка авторизирован ли пользователь под данным телеграм кодом
def is_telegram_id_set(user:WPUser, telegram_id:int):
    usermeta = session.query(WPUserMeta).filter_by(user_id=user.ID, user_meta_key=TELEGRAM_ID).first()
    session.close()
    if usermeta and int(usermeta.user_meta_value) == telegram_id:
        return True
    return False
    
# Запросы изменений
# Создание резервации места на парковке (Если вернет False резервация не удалась)
def add_reserves(user:WPUser, hours_count:int):
    try:
        now = datetime.now()
        timestamp_begin = now.timestamp();
        timestamp_end = (now + timedelta(hours=hours_count)).timestamp();
        filter_condition = (WPReserve.reserve_begin.between(timestamp_begin, timestamp_end)) | \
                           (WPReserve.reserve_end.between(timestamp_begin, timestamp_end))
        

        occupied_place_ids = session.query(WPReserve.place_id).filter(WPReserve.reserve_is_deleted == 0).all()

        # Get the unoccupied parking places
        available_places = session.query(WPPlace).filter(~WPPlace.ID.in_(occupied_place_ids)).first()
        print("\n\nplaces = ", available_places.place_code, "\n\n")
        return None
        # reserves = session.query(WPReserve.place).filter(filter_condition & \
        #                             WPReserve.reserve_is_deleted == 0)
        # if(reserves.count() > 0):
        #     occupied_place_codes = [place_code for (place_code,) in reserves]
        #     place = session.query(WPPlace).filter(~WPPlace.place_code.in_(occupied_place_codes)).first()
        #     # place = session.query(WPPlace).filter((WPPlace != reserve.place for reserve in reserves.all())).first()
        #     print("\n\n", reserves.all(), "\n\nPlace = ", place.place_code, "\n\n")
            
        # else:
        #     place = session.query(WPPlace).first()
        
        # if(not place):
        #     return None
        
        # new_reserve = WPReserve(
        #     reserve_begin=timestamp_begin,
        #     reserve_end=timestamp_end,
        #     place_id=place.ID,
        #     user_id = user.ID,
        # )
        # if sql_add(new_reserve):
        #     return place
    except Exception as e:
        print("\n\nadd_reserve\n", e, "\n\n\n")
        return None
# Удаление резервации   
def delete_reserves(user:WPUser, place:WPPlace):
    filter_condition = (WPReserve.reserve_end < datetime.now()) & (WPReserve.user_id == user.ID) & (WPReserve.place_id == place.ID)
    reserve = session.query(WPReserve).filter(filter_condition & (not WPReserve.reserve_is_deleted)).first()

    if(reserve):
        remove_row(reserve)
        session.close()
        return True
    return False
# Сохранение телеграм кода пользователя как авторизированного
def save_telegram_id(user:WPUser, telegram_id:int):
    usermeta = session.query(WPUserMeta).filter((WPUserMeta.user_id == user.ID) & (WPUserMeta.user_meta_key == TELEGRAM_ID)).first()

    if usermeta:
        usermeta.user_meta_value = telegram_id
    else:
        usermeta = WPUserMeta(user_id=user.ID, user_meta_key=TELEGRAM_ID, user_meta_value=telegram_id)
        session.add(usermeta)

    session.commit()

    session.close()
# Сохранение сообщения в базе данных
def save_user_message(my_message: Message, bot_message: Message, user_id: int, answer_id: Optional[int]):
    try:
        db_message = WPMessage(
            message_date=my_message.date.utcnow().timestamp(),
            message_user_telegram_id=my_message.from_user.id,
            message_bot_telegram_id = bot_message.message_id,
            message_telegram_id=my_message.message_id,
            message_text=my_message.text,
            message_answer_id=answer_id,
            user_id=user_id
        )
        session.add(db_message)
        session.commit()
        session.close()
    except Exception as e:
        print(e)
        return None

def save_file(file: WPDocument):
    sql_add(file)
