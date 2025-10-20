from database import Base, engine
from models import User, Todo

def init():
    print("Tworzenie bazy danych...")
    Base.metadata.create_all(bind=engine)
    print("Baza danych gotowa!")

if __name__ == "__main__":
    init()
