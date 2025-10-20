# main.py
from fastapi import FastAPI, Depends, HTTPException, Header, Request, Cookie, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional, List

# --- DATABASE ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# --- MODELS ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    todos = relationship("Todo", back_populates="owner")

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="todos")

Base.metadata.create_all(bind=engine)

# --- SCHEMAS ---
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = ""

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class TodoPatch(BaseModel):
    completed: Optional[bool] = None
    description: Optional[str] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    owner_id: int
    class Config:
        from_attributes = True

# --- APP ---
app = FastAPI()

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PASSWORD ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# --- JWT ---
SECRET_KEY = "supersekretnyklucz"
ALGORITHM = "HS256"
def create_access_token(username: str, expires_minutes: int = 60*24):
    to_encode = {"sub": username, "exp": datetime.utcnow() + timedelta(minutes=expires_minutes)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# --- DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- HELPERS: extract token ---
def extract_token(
    authorization: Optional[str] = Header(None),
    token_header: Optional[str] = Header(None, alias="token"),
    token_header_cap: Optional[str] = Header(None, alias="Token"),
    cookie_token: Optional[str] = Cookie(None, alias="token"),
    query_token: Optional[str] = Query(None, alias="token"),
) -> Optional[str]:
    if authorization:
        if authorization.lower().startswith("bearer "):
            return authorization[7:].strip()
        return authorization.strip()
    if token_header:
        return token_header.strip()
    if token_header_cap:
        return token_header_cap.strip()
    if cookie_token:
        return cookie_token.strip()
    if query_token:
        return query_token.strip()
    return None

# --- EXCEPTION HANDLER ---
@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={"Access-Control-Allow-Origin": "*"},
    )

# --- AUTH ROUTES ---
@app.post("/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="username and password required")
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = hash_password(user.password)
    new_user = User(username=user.username, password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token(new_user.username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}

# --- AUTH UTIL ---
def get_current_user(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
    token_header: Optional[str] = Header(None, alias="token"),
    token_header_cap: Optional[str] = Header(None, alias="Token"),
    cookie_token: Optional[str] = Cookie(None, alias="token"),
    query_token: Optional[str] = Query(None, alias="token"),
) -> User:
    raw = extract_token(authorization, token_header, token_header_cap, cookie_token, query_token)
    if not raw:
        raise HTTPException(status_code=401, detail="Missing token")
    username = decode_access_token(raw)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# --- TODOS ---
@app.get("/todos", response_model=List[TodoResponse])
def get_todos(current_user: User = Depends(get_current_user)):
    return current_user.todos

@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_todo = Todo(title=todo.title, description=todo.description or "", owner_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.title is not None:
        db_todo.title = todo.title
    if todo.description is not None:
        db_todo.description = todo.description
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def patch_todo(todo_id: int, data: TodoPatch, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if data.completed is not None:
        db_todo.completed = data.completed
    if data.description is not None:
        db_todo.description = data.description
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"detail": "Todo deleted"}
