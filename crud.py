from sqlalchemy.orm import Session
from models import User, Todo

def get_user_by_login(db: Session, login: str):
    return db.query(User).filter(User.login == login).first()

def create_user(db: Session, login: str, password: str):
    user = User(login=login, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_todos(db: Session, user_id: int):
    return db.query(Todo).filter(Todo.user_id == user_id).all()

def create_todo(db: Session, title: str, user_id: int):
    todo = Todo(title=title, user_id=user_id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo
