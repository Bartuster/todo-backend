from sqlalchemy import Column, Integer, String, Boolean
from database import Base  # to musi być SQLAlchemy declarative_base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    completed = Column(Boolean, default=False)
