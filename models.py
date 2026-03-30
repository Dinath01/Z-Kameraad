from sqlalchemy import Column, String, Integer
from database import Base


# User Model

class User(Base):
    __tablename__ = "users"

    # Core user fields
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

    # Optional profile info (used for peers)
    name = Column(String, nullable=True)
    bio = Column(String, nullable=True)

    # Activity tracking
    sessions = Column(Integer, default=0)

    # Status flags (0 = false, 1 = true)
    is_online = Column(Integer, default=0)
    is_busy = Column(Integer, default=0)


# Chat Model

class Chat(Base):
    __tablename__ = "chats"

    # Chat session identifiers
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String)
    peer_id = Column(String)

    # Chat state (1 = active, 0 = ended)
    is_active = Column(Integer, default=1)