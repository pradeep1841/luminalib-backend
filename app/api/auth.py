from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import SessionLocal
from app.core.security import create_token, hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin

router = APIRouter()


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)

    new_user = User(email=user.email, password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # user find karo
    db_user = db.query(User).filter(User.email == user.email).first()

    # user exist nahi karta
    if not db_user:
        return {"error": "User not found"}

    # password check karo
    if db_user.password != hash_password(user.password):
        return {"error": "Invalid password"}

    # token create karo
    token = create_token({"sub": user.email})

    return {"access_token": token}


@router.get("/profile")
def profile(user=Depends(get_current_user)):
    return {"message": "You are logged in", "user": user}
