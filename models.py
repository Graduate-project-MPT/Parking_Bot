from sqlalchemy import create_engine, Column, Integer, String, Text, BigInteger, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

from config import settings

Base = declarative_base()
engine = create_engine(settings.CON_STRING, echo=True, connect_args={'user': 'root', 'password': 'root'})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, expire_on_commit=False)
session = Session()

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

class WPUserMeta(Base):
    __tablename__ = 'wp_usermeta'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('wp_users.ID'), nullable=False)
    user_meta_key = Column(String(100), nullable=True)
    user_meta_value = Column(Text, nullable=True)
    user = relationship('WPUser', back_populates='usermeta')

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

class WPDocument(Base):
    __tablename__ = 'wp_document'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, ForeignKey('wp_message.ID'), nullable=False)
    document_file_id = Column(String(100), nullable=True)
    document_file_unique_id = Column(String(100), nullable=True)
    document_file_size = Column(BigInteger, nullable=False)
    document_file_url = Column(Text, nullable=True)
    document_file_mime = Column(Text, nullable=True)

class WPDocumentMeta(Base):
    __tablename__ = 'wp_documentmeta'

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, ForeignKey('wp_message.ID'), nullable=False)
    document_meta_key = Column(String(100), nullable=True)
    document_meta_value = Column(Text, nullable=True)

def get_users():
    user = session.query(WPUser)
    session.close()
    return user