from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from crud import get_todos, create_todo, update_todo, delete_todo, get_user_by_login
from database import SessionLocal
from schemas import TodoCreate, TodoUpdate, TodoOut, UserOut
from auth import decode_access_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    login = decode_access_token(token)
    if not login:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_login(db, login)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/todos/", response_model=list[TodoOut])
def read_todos(current_user: UserOut = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_todos(db, current_user.id)

@router.post("/todos/", response_model=TodoOut)
def create_todo_endpoint(todo: TodoCreate, current_user: UserOut = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_todo(db, todo, current_user.id)

@router.put("/todos/{todo_id}", response_model=TodoOut)
def update_todo_endpoint(todo_id: int, todo: TodoUpdate, current_user: UserOut = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = update_todo(db, todo_id, todo)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@router.delete("/todos/{todo_id}", response_model=TodoOut)
def delete_todo_endpoint(todo_id: int, current_user: UserOut = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = delete_todo(db, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo
