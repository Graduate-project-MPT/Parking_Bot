from sqlalchemy import \
    Column, Integer, Boolean, String, Text, BigInteger, \
    ForeignKey, TIMESTAMP, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

from config import settings

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
    reserve_end = Column(BigInteger, nullable=False)
    reserve_is_deleted = Column(Boolean, nullable=False, default=False)
    reserve_is_started = Column(Boolean, nullable=False, default=False)

    place_id = Column(BigInteger,
                      ForeignKey('wp_place.ID'), nullable=True)
    user_id = Column(BigInteger,
                     ForeignKey('wp_user.ID'), nullable=False)

    place = relationship('WPPlace', back_populates='reserve')
