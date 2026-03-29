from fastapi import FastAPI
from auth_routes import router as auth_router
from pydantic import BaseModel
from typing import List
from datetime import datetime
from predict_routes import router as predict_router
from fastapi import HTTPException
from match_routes import router as match_router
from chat_routes import router as chat_router
from state import active_chats, pending_requests, online_peers, chat_messages


app = FastAPI(title="Z Kameraad Burnout API")

from predict_routes import router as predict_router

app.include_router(predict_router)

app.include_router(auth_router)

app.include_router(match_router)

app.include_router(chat_router)


class BurnoutRequest(BaseModel):
    text: str


class BurnoutResponse(BaseModel):
    burnout_level: int
    burnout_meaning: str
    confidence: List[float]


class PeerAvailabilityRequest(BaseModel):
    peer_id: str
    online: bool


class MatchRequest(BaseModel):
    user_id: str
    burnout_level: int


class MatchAcceptRequest(BaseModel):
    peer_id: str
    user_id: str

class EndChatRequest(BaseModel):
    chat_id: str
    ended_by: str


def map_label(label: int) -> str:
    return {
        0: "No burnout detected",
        1: "Mild burnout detected",
        2: "High burnout detected",
    }.get(label, "Unknown")


@app.get("/")
def root():
    return {"status": "Z Kameraad backend running"}

@app.post("/predict", response_model=BurnoutResponse)
def predict_burnout(request: BurnoutRequest):
    result = burnout_model.predict(request.text)
    label = result["label"]

    return {
        "burnout_level": label,
        "burnout_meaning": map_label(label),
        "confidence": result["confidence"],
    }


@app.post("/peer/availability")
def set_peer_availability(data: PeerAvailabilityRequest):
    if data.online:
        online_peers.add(data.peer_id)
    else:
        online_peers.discard(data.peer_id)

    return {
        "peer_id": data.peer_id,
        "online": data.online,
        "online_peers": list(online_peers),
    }


@app.post("/match/request")
def request_peer(data: MatchRequest):
    if not online_peers:
        return {"status": "no_peers"}

    assigned_peer = next(iter(online_peers))

    online_peers.remove(assigned_peer)

    pending_requests[assigned_peer] = data.user_id

    return {
        "status": "pending",
        "peer_id": assigned_peer,
    }


@app.get("/peer/requests")
def get_peer_requests(peer_id: str):
    for chat in active_chats.values():
        if chat["peer_id"] == peer_id:
            return {"has_request": False}

    user_id = pending_requests.get(peer_id)

    if not user_id:
        return {"has_request": False}

    return {
        "has_request": True,
        "user_id": user_id,
    }


@app.post("/match/accept")
def accept_match(data: MatchAcceptRequest):
    for chat in active_chats.values():
        if chat["peer_id"] == data.peer_id:
            return {
                "status": "already_in_chat"
            }

    chat_id = f"chat_{len(active_chats) + 1}"

    active_chats[chat_id] = {
        "peer_id": data.peer_id,
        "user_id": data.user_id,
    }

    pending_requests.pop(data.peer_id, None)

    return {
        "chat_id": chat_id,
    }


@app.get("/match/status")
def check_match_status(user_id: str):
    for chat_id, chat in active_chats.items():
        if chat["user_id"] == user_id:
            return {
                "matched": True,
                "chat_id": chat_id,
            }

    return {"matched": False}



class ChatMessageRequest(BaseModel):
    chat_id: str
    sender_id: str
    text: str

@app.post("/chat/send")
def send_message(data: ChatMessageRequest):
    if data.chat_id not in chat_messages:
        chat_messages[data.chat_id] = []

    chat_messages[data.chat_id].append({
        "sender_id": data.sender_id,
        "text": data.text,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {"status": "sent"}

@app.get("/chat/messages")
def get_messages(chat_id: str):
    return {
        "messages": chat_messages.get(chat_id, [])
    }

@app.post("/chat/end")
def end_chat(data: EndChatRequest):
    chat = active_chats.get(data.chat_id)

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    peer_id = chat["peer_id"]

    online_peers.add(peer_id)

    active_chats.pop(data.chat_id, None)
    chat_messages.pop(data.chat_id, None)

    return {
        "status": "ended",
        "peer_id": peer_id,
    }

#feedback

class FeedbackRequest(BaseModel):
    chat_id: str
    from_role: str 
    rating: int
    comment: str | None = None


chat_feedback: dict[str, list[dict]] = {}


@app.post("/chat/feedback")
def submit_feedback(data: FeedbackRequest):
    if data.chat_id not in chat_feedback:
        chat_feedback[data.chat_id] = []

    chat_feedback[data.chat_id].append({
        "from_role": data.from_role,
        "rating": data.rating,
        "comment": data.comment,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {"status": "ok"}
