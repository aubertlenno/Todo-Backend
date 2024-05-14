from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List
from datetime import datetime
from models import Base, UserDB, TodoDB
from schemas import User, Todo
from auth import get_db, create_user, verify_user

# Constants
SECRET = "Pangx9D9QkUU91mtMIFY-Iv6AmQcg4wkr1SdrWEeeZk"
DATABASE_URL = ""

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# App initialization
app = FastAPI(
    title="Todo API",
    description="API for managing todos with authentication",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "users",
            "description": "Operations with users.",
        },
        {
            "name": "todos",
            "description": "Manage todos.",
        },
    ],
)

# CORS setup
origins = [
    "http://localhost:5173",  # Add your frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow specific origins
    allow_credentials=True,  # Allow credentials (cookies, etc.)
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Login Manager
manager = LoginManager(SECRET, '/login', use_cookie=True)
manager.cookie_name = "auth_cookie"

# Ensure user_loader is defined and registered
@manager.user_loader
def load_user(username: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post('/register', tags=["users"])
def register_user(user: User, db: Session = Depends(get_db)):
    return create_user(user, db)

@app.post('/login', tags=["users"])
def login_user(data: User, response: Response, db: Session = Depends(get_db)):
    user = verify_user(data, db)
    if not user:
        raise InvalidCredentialsException
    access_token = manager.create_access_token(data={'sub': user.username})
    manager.set_cookie(response, access_token)
    response.set_cookie(key="auth_cookie", value=access_token, httponly=True, samesite='Lax')
    return {"msg": "Login successful"}

@app.post('/logout', tags=["users"])
def logout_user(response: Response):
    response.delete_cookie("auth_cookie")
    return {"msg": "Logout successful"}

@app.get('/protected', tags=["users"])
def protected_route(user=Depends(manager)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    return {"msg": f"Hello {user.username}, you are authenticated"}

# Todo Endpoints
@app.post("/todos/", response_model=Todo, tags=["todos"])
def create_todo(todo: Todo, db: Session = Depends(get_db), user=Depends(manager)):
    db_todo = TodoDB(text=todo.text, completed=todo.completed, time=todo.time)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/", response_model=List[Todo], tags=["todos"])
def read_todos(db: Session = Depends(get_db), user=Depends(manager)):
    todos = db.query(TodoDB).all()
    return todos

@app.get("/todos/{todo_id}", response_model=Todo, tags=["todos"])
def read_todo_by_id(todo_id: int, db: Session = Depends(get_db), user=Depends(manager)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}/update_text/", response_model=Todo, tags=["todos"])
def update_todo_text(todo_id: int, text: str, db: Session = Depends(get_db), user=Depends(manager)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.text = text
    db.commit()
    db.refresh(todo)
    return todo

@app.put("/todos/{todo_id}/update_status/", response_model=Todo, tags=["todos"])
def update_todo_status(todo_id: int, completed: bool, db: Session = Depends(get_db), user=Depends(manager)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.completed = completed
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/todos/{todo_id}", tags=["todos"])
def delete_todo_by_id(todo_id: int, db: Session = Depends(get_db), user=Depends(manager)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

@app.delete("/todos/text/{text}", tags=["todos"])
def delete_todo_by_text(text: str, db: Session = Depends(get_db), user=Depends(manager)):
    todos = db.query(TodoDB).filter(TodoDB.text == text).all()
    if not todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    for todo in todos:
        db.delete(todo)
    db.commit()
    return {"message": "Todo(s) deleted successfully"}

@app.delete("/todos/", tags=["todos"])
def delete_all_todos(db: Session = Depends(get_db), user=Depends(manager)):
    db.query(TodoDB).delete()
    db.commit()
    return {"message": "All todos deleted successfully"}
