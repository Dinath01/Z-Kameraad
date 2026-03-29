from fastapi import APIRouter
from pydantic import BaseModel
from matching import match_peer
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User

router = APIRouter()

class MatchInput(BaseModel):
    burnout_level: int

@router.post("/match")
def match(input: MatchInput):
    result = match_peer(input.burnout_level)
    return result

from state import online_peers, pending_requests

@router.post("/request-specific")
def request_specific(data: dict):
    user_id = data.get("user_id")
    peer_id = data.get("peer_id")

    # check if peer is online
    if peer_id not in online_peers:
        return {"status": "unavailable"}

    # assign request
    pending_requests[peer_id] = user_id

    # remove from available pool (same as broadcast)
    online_peers.discard(peer_id)

    return {"status": "sent"}