import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'db.sqlite3')
conn = sqlite3.connect(DB)
cur = conn.cursor()
updates = [
    ('cart_cart', 'user_id', 'ALTER TABLE cart_cart ADD COLUMN user_id integer'),
    ('cart_cart', 'session_key', 'ALTER TABLE cart_cart ADD COLUMN session_key varchar(40)'),
    ('cart_cart', 'is_active', 'ALTER TABLE cart_cart ADD COLUMN is_active bool DEFAULT 1'),
    ('cart_cart', 'created_at', 'ALTER TABLE cart_cart ADD COLUMN created_at datetime'),
    ('cart_cart', 'updated_at', 'ALTER TABLE cart_cart ADD COLUMN updated_at datetime'),
    ('cart_cartitem', 'unit_price', 'ALTER TABLE cart_cartitem ADD COLUMN unit_price decimal(12,2)'),
    ('cart_cartitem', 'added_at', 'ALTER TABLE cart_cartitem ADD COLUMN added_at datetime'),
    ('cart_cartitem', 'updated_at', 'ALTER TABLE cart_cartitem ADD COLUMN updated_at datetime'),
]
for table, col, sql in updates:
    cur.execute(f"PRAGMA table_info({table})")
    existing = [row[1] for row in cur.fetchall()]
    if col not in existing:
        print(f"Adding {col} to {table}")
        cur.execute(sql)
    else:
        print(f"Already has {col} in {table}")

cur.execute("UPDATE cart_cart SET session_key=substr(cart_id,1,40), is_active=1, created_at=date_added, updated_at=date_added WHERE session_key IS NULL OR session_key=''")
conn.commit()

print('cart_cart columns:')
cur.execute('PRAGMA table_info(cart_cart)')
print(cur.fetchall())
print('cart_cartitem columns:')
cur.execute('PRAGMA table_info(cart_cartitem)')
print(cur.fetchall())
conn.close()
