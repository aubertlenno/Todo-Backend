from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models import UserDB
from schemas import User
import bcrypt

def create_user(user: User, db: Session):
    if db.query(UserDB).filter(UserDB.email == user.email).first():
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = UserDB(username=user.username, password=hashed_password.decode('utf-8'), email=user.email)
    db.add(db_user)
    db.commit()
    return {"msg": "User registered successfully"}

def verify_user(data: User, db: Session):
    user = db.query(UserDB).filter(UserDB.username == data.username).first()
    if user and bcrypt.checkpw(data.password.encode('utf-8'), user.password.encode('utf-8')):
        return user
    return None

def get_db():
    from main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()