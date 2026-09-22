import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS placements")

cursor.execute("""
CREATE TABLE placements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placement_id TEXT UNIQUE,
    platform TEXT,
    post_name TEXT,
    cost REAL,
    date TEXT
)
""")

conn.commit()
conn.close()

print("Таблица placements обновлена!")