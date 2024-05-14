from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class Todo(BaseModel):
    id: Optional[int] = None
    text: str
    completed: bool = False
    time: datetime