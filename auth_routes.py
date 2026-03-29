import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from auth_utils import hash_password, verify_password, create_access_token
from models import User, Chat


from database import SessionLocal, engine
from models import User
from auth_utils import hash_password, verify_password, create_access_token

User.metadata.create_all(bind=engine)

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str

    name: str | None = None
    bio: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,

        name=data.name if data.role == "peer" else None,
        bio=data.bio if data.role == "peer" else None,
    )

    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.id, "role": user.role})

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "token": token,
        "name": user.name,
        "bio": user.bio,
        "token": token,
    }

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.id, "role": user.role})

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "token": token,
    }

@router.get("/peers")
def get_peers(db: Session = Depends(get_db)):
    peers = db.query(User).filter(User.role == "peer").all()

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
    chat_id = data.get("chat_id")

    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        return {"status": "chat not found"}

    peer = db.query(User).filter(User.id == chat.peer_id).first()

    if peer:
        peer.is_busy = 0  # 🔥 FREE THE PEER

    chat.is_active = 0

    db.commit()

    return {"status": "ended"}
