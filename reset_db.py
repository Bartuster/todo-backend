# reset_db.py
import os
from database import Base, engine

# Usuń starą bazę, jeśli istnieje
if os.path.exists("todo.db"):
    os.remove("todo.db")
    print("Stara baza została usunięta.")

# Stwórz wszystkie tabele według modeli
Base.metadata.create_all(bind=engine)
print("Nowa baza i tabele zostały utworzone.")
