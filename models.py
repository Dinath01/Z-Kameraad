from sqlalchemy import Column, String, Integer
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

    
    name = Column(String, nullable=True)
    bio = Column(String, nullable=True)

    
    sessions = Column(Integer, default=0)

    is_online = Column(Integer, default=0)  # 0 = offline, 1 = online
    is_busy = Column(Integer, default=0)
    

from sqlalchemy import Column, String, Integer

class Chat(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String)
    peer_id = Column(String)
    is_active = Column(Integer, default=1)