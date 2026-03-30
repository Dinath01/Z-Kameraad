from fastapi import APIRouter
from state import active_chats

# Router for chat-related endpoints
router = APIRouter()


@router.get("/chat-status/{chat_id}")
def chat_status(chat_id: str):
    """
    Check whether a chat session is currently active.
    """
    return {
        "active": chat_id in active_chats
    }