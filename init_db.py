import os
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# --- USUŃ starą bazę jeśli istnieje ---
if os.path.exists("todo.db"):
    os.remove("todo.db")
    print("Stara baza usunięta.")

# --- NOWA BAZA ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# --- MODELE ---
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
    description = Column(String, default="")  # ✅ NOWA KOLUMNKA
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="todos")

# --- UTWÓRZ WSZYSTKO ---
Base.metadata.create_all(bind=engine)
print("Nowa baza todo.db została utworzona z kolumną description.")
