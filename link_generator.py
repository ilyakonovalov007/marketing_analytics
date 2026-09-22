import sqlite3

BOT_USERNAME = "marketing_analytics_test_bot"

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

platform = input("Площадка: ")
post_name = input("Название поста: ")
cost = float(input("Стоимость размещения: "))

cursor.execute("""
SELECT COUNT(*) FROM placements
""")

count = cursor.fetchone()[0]

placement_id = f"placement_{count + 1:03d}"

cursor.execute("""
INSERT INTO placements
(placement_id, platform, post_name, cost, date)
VALUES (?, ?, ?, ?, datetime('now'))
""", (
    placement_id,
    platform,
    post_name,
    cost
))

conn.commit()

link = f"https://t.me/{BOT_USERNAME}?start={placement_id}"

print("\nРазмещение создано!")
print("ID:", placement_id)
print("Ссылка:", link)

conn.close()