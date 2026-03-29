from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Chat
import uuid

router = APIRouter()

from state import active_chats  

@router.get("/chat-status/{chat_id}")
def chat_status(chat_id: str):
    return {
        "active": chat_id in active_chats
    }

