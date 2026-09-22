import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM payments")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()