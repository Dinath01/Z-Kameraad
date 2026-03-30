import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal, engine
from models import User, Chat
from auth_utils import hash_password, verify_password, create_access_token

# Ensure database tables are created
User.metadata.create_all(bind=engine)

# Router configuration for authentication-related endpoints
router = APIRouter(prefix="/auth", tags=["Auth"])


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Request model for user registration
class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str
    name: str | None = None
    bio: str | None = None


# Request model for user login
class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email already exists
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        # Only peers have name and bio
        name=data.name if data.role == "peer" else None,
        bio=data.bio if data.role == "peer" else None,
    )

    db.add(user)
    db.commit()

    # Generate authentication token
    token = create_access_token({"sub": user.id, "role": user.role})

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "token": token,
        "name": user.name,
        "bio": user.bio,
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Validate user credentials
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate authentication token
    token = create_access_token({"sub": user.id, "role": user.role})

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "token": token,
    }


@router.get("/peers")
def get_peers(db: Session = Depends(get_db)):
    # Fetch all users with role "peer"
    peers = db.query(User).filter(User.role == "peer").all()

    # Return relevant peer details
    return [
        {
            "id": p.id,
            "name": p.name,
            "bio": p.bio,
            "sessions": p.sessions,
            "is_online": p.is_online,
            "is_busy": p.is_busy,
        }
        for p in peers
    ]


@router.post("/end-chat")
def end_chat(data: dict, db: Session = Depends(get_db)):
    # Get chat ID from request body
    chat_id = data.get("chat_id")

    # Find the chat session
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        return {"status": "chat not found"}

    # Free the peer assigned to the chat
    peer = db.query(User).filter(User.id == chat.peer_id).first()
    if peer:
        peer.is_busy = 0

    # Mark chat as inactive
    chat.is_active = 0

    db.commit()

    return {"status": "ended"}