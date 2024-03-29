from sqlalchemy import create_engine, Column, Integer, String, Text, BigInteger, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

from config import settings
from datetime import timedelta, datetime

Base = declarative_base()
engine = create_engine(settings.CON_STRING, echo=True, connect_args={'user': 'root', 'password': 'root'})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, expire_on_commit=False)
session = Session()

# Класс пользователя
class WPUser(Base):
    __tablename__ = 'wp_users'

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
    messages = relationship('WPMessage', back_populates='user')

    # Добавляем отношение reserve
    reserves = relationship('WPReserve', back_populates='user')
# Класс мета данных пользователя
class WPUserMeta(Base):
    __tablename__ = 'wp_usermeta'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('wp_users.ID'), nullable=False)
    user_meta_key = Column(String(100), nullable=True)
    user_meta_value = Column(Text, nullable=True)

    user = relationship('WPUser', back_populates='usermeta')
# Класс сообщений
class WPMessage(Base):
    __tablename__ = 'wp_message'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    message_date = Column(BigInteger, nullable=True)
    user_id = Column(BigInteger, ForeignKey('wp_users.ID'), nullable=True)
    telegram_message_id = Column(BigInteger, nullable=False)
    message_text = Column(Text, nullable=True)
    message_answer_id = Column(BigInteger, ForeignKey('wp_message.ID'), nullable=True)
    
    user = relationship('WPUser', back_populates='messages')
    message_answer = relationship('WPMessage', remote_side=[ID])
    document = relationship('WPDocument', back_populates='message')
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

    messagge = relationship('WPMessage', back_populates='document')
# Класс парковочных мест
class WPPlace(Base):
    __tablename__ = 'wp_place'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    place_is_valid = Column(bool, nullable=False)
    place_code = Column(String(4), nullable=False)
    
    reserve = relationship('WPReserve', back_populates='place')
# Класс резервации парковочных мест
class WPReserve(Base):
    __tablename__ = 'wp_reserve'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    reserve_begin = Column(BigInteger, nullable=False)
    reserve_end = Column(BigInteger, nullable=True)
    reserve_is_deleted = Column(bool, nullable=False, default=0)
    
    place_id = Column(BigInteger, ForeignKey('wp_place.ID'), nullable=True)
    user_id = Column(bool, ForeignKey('wp_user.ID'), nullable=False)
    
    place = relationship('WPPlace', back_populates='reserve')

# Добавляет запись в БД
def sql_add(data):
    try:
        session.add(data)
        session.commit()
        session.close()
        return True
    except Exception as e:
        print(e)
        return False
# Удаляет запись бд
def remove_row(data):
    session.delete(data)
    session.commit()

# Возвращает запись пользователя по его логину
def find_user_by_login(login:str):
    user = session.query(WPUser).filter_by(user_login=login).first()
    session.close()
    return user
# Возвращает парковочное место по его наименованию
def find_place_by_code(place_code:str):
    filter_condition =  (WPPlace.place_code == place_code)
    return session.query(WPPlace).filter(filter_condition).first()
# Возвращает мета запись телеграм кода
def find_user_by_telegram_id(telegram_id:int):
    try:
        filter_condition =  (WPUserMeta.user_meta_value == telegram_id) & \
                            (WPUserMeta.user_meta_key == 'telegram_id')
        meta = session.query(WPUserMeta).filter(filter_condition).first()
        return meta
    except:
        return None
# Возвращает актуальные резервации по телеграм коду авторизированного подльзователя
def find_actual_reserves(user:WPUser, is_deleted:bool = False):
    actual_timestamp = datetime.now();
    try:
        filter_condition =  (WPReserve.user_id == user.ID) & \
                            (WPReserve.reserve_end > actual_timestamp) & \
                            (WPReserve.reserve_begin < actual_timestamp) & \
                            (WPReserve.reserve_is_deleted == is_deleted)
        return session.query(WPReserve).filter(filter_condition).all()
    except:
        return None
# Возвращает все резервации по телеграм коду авторизированного подльзователя
def find_reserves(user:WPUser, is_deleted:bool = False):
    try:
        filter_condition =  (WPReserve.user_id == user.ID) & \
                            (WPReserve.reserve_is_deleted == is_deleted)
        return session.query(WPReserve).filter(filter_condition).all()
    except:
        return None
# Возвращает место по его коду
def find_place_by_id(place_id:int, is_deleted:bool = False):
    filter_condition =  (WPPlace.ID==place_id)
    place = session.query(WPPlace).filter_by(filter_condition).first()
    session.close()
    return place

# Проерка авторизирован ли пользователь под данным телеграм кодом
def is_telegram_id_set(user:WPUser, telegram_id:int):
    try:
        usermeta = session.query(WPUserMeta).filter_by(user_id=user.ID, user_meta_key='telegram_id').first()
        session.close()
        if usermeta and int(usermeta.user_meta_value) == telegram_id:
            return True
        return False
    except:
        return False
    
# Создание резервации места на парковке (Если вернет False резервация не удалась)
def add_reserves(user:WPUser, hours_count:int):
    try:
        timestamp_begin = datetime.now();
        timestamp_end = timestamp_begin + timedelta(hours=hours_count);
        filter_condition = (WPReserve.reserve_begin.between(timestamp_begin, timestamp_end)) | (WPReserve.reserve_end.between(timestamp_begin, timestamp_end))
        
        reserves = session.query(WPReserve).filter(filter_condition & (not WPReserve.reserve_is_deleted)).all()

        place = session.query(WPPlace).filter(not any(WPPlace.ID == reserve.place_id for reserve in reserves)).first()

        if(not place):
            return False
        
        new_reserve = WPReserve(
            reserve_begin=timestamp_begin,
            reserve_end=timestamp_end,
            place_id=place.ID,
            user_id = user.ID
        )
        if sql_add(new_reserve):
            return place
    except:
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
    usermeta = session.query(WPUserMeta).filter_by(user_id=user.ID, user_meta_key='telegram_id').first()

    if usermeta:
        usermeta.user_meta_value = telegram_id
    else:
        usermeta = WPUserMeta(user_id=user.ID, user_meta_key='telegram_id', user_meta_value=telegram_id)
        session.add(usermeta)

    session.commit()

    session.close()

