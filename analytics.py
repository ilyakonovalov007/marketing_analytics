import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
SELECT
    p.placement_id,
    p.platform,
    p.post_name,
    p.cost,

    COUNT(DISTINCT l.id) AS leads,
    COUNT(DISTINCT pay.id) AS payments,
    COALESCE(SUM(pay.amount), 0) AS revenue

FROM placements p

LEFT JOIN leads l
    ON p.placement_id = l.source

LEFT JOIN payments pay
    ON p.placement_id = pay.placement_id

GROUP BY
    p.placement_id,
    p.platform,
    p.post_name,
    p.cost
""")

rows = cursor.fetchall()

for row in rows:
    placement_id, platform, post_name, cost, leads, payments, revenue = row

    if leads > 0:
        conversion = payments / leads * 100
    else:
        conversion = 0

    if cost > 0:
        romi = (revenue - cost) / cost * 100
    else:
        romi = 0

    print("=" * 40)
    print(f"Размещение: {placement_id}")
    print(f"Площадка: {platform}")
    print(f"Пост: {post_name}")
    print()
    print(f"Расход на рекламу: {cost:,.0f} ₽")
    print(f"Лиды: {leads}")
    print(f"Покупки: {payments}")
    print(f"Конверсия лид → покупка: {conversion:.1f}%")
    print(f"Выручка: {revenue:,.0f} ₽")
    print(f"ROMI: {romi:.1f}%")
    print("=" * 40)

conn.close()