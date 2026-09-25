import sqlite3
import os

db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(cart_cart);")
    columns = cursor.fetchall()
    print("cart_cart columns:")
    for col in columns:
        print(col)
    conn.close()
