import sqlite3

# Połączenie z bazą
conn = sqlite3.connect("todo.db")
cursor = conn.cursor()

# Sprawdzenie, czy kolumna już istnieje
cursor.execute("PRAGMA table_info(todos);")
columns = [col[1] for col in cursor.fetchall()]

if "owner_id" not in columns:
    cursor.execute("ALTER TABLE todos ADD COLUMN owner_id INTEGER;")
    print("Kolumna owner_id została dodana.")
else:
    print("Kolumna owner_id już istnieje.")

# Zamknięcie połączenia
conn.commit()
conn.close()
