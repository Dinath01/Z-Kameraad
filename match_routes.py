from fastapi import APIRouter
from pydantic import BaseModel

from matching import match_peer
from state import online_peers, pending_requests

# Router for matching-related endpoints
router = APIRouter()


# Request model for general matching
class MatchInput(BaseModel):
    burnout_level: int


@router.post("/match")
def match(input: MatchInput):
    """
    Match a user with a peer based on burnout level.
    """
    return match_peer(input.burnout_level)


@router.post("/request-specific")
def request_specific(data: dict):
    """
    Send a request to a specific peer if they are online.
    """
    user_id = data.get("user_id")
    peer_id = data.get("peer_id")

    # Check if the peer is available
    if peer_id not in online_peers:
        return {"status": "unavailable"}

    # Assign request to the selected peer
    pending_requests[peer_id] = user_id

    # Remove peer from available pool
    online_peers.discard(peer_id)

    return {"status": "sent"}