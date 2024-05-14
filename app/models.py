from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(100))
    email = Column(String(100), unique=True, index=True)

class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), index=True)
    completed = Column(Boolean, default=False)
    time = Column(DateTime, default=datetime.utcnow)