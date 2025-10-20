# create_db.py
from database import Base, engine
from models import User, Todo

Base.metadata.create_all(bind=engine)
print("Database tables created.")
