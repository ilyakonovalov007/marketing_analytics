import sqlite3
from datetime import datetime

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Показываем существующие лиды
cursor.execute("""
SELECT id, user_id, name, contact, source
FROM leads
""")

leads = cursor.fetchall()

if not leads:
    print("Пока нет ни одного лида.")
    conn.close()
    exit()

print("\nДоступные лиды:\n")

for lead in leads:
    lead_id, user_id, name, contact, source = lead

    print(
        f"{lead_id}. "
        f"{name} | "
        f"{contact} | "
        f"{source}"
    )

# Выбираем лида
lead_id = int(input("\nВыберите ID лида: "))

cursor.execute("""
SELECT user_id, source
FROM leads
WHERE id = ?
""", (lead_id,))

result = cursor.fetchone()

if not result:
    print("Такого лида нет.")
    conn.close()
    exit()

user_id, placement_id = result

# Данные покупки
amount = float(input("Сумма покупки: "))
course = input("Курс: ")

# Сохраняем платёж
cursor.execute("""
INSERT INTO payments
(user_id, placement_id, amount, course, date)
VALUES (?, ?, ?, ?, ?)
""", (
    user_id,
    placement_id,
    amount,
    course,
    str(datetime.now())
))

conn.commit()

print("\nПлатёж сохранён!")
print(f"Пользователь: {user_id}")
print(f"Источник: {placement_id}")
print(f"Сумма: {amount:.0f} ₽")
print(f"Курс: {course}")

conn.close()