import sqlite3
import os

db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cart_cart;")
    count = cursor.fetchone()[0]
    print(f"Number of rows in cart_cart: {count}")
    
    cursor.execute("SELECT * FROM cart_cart LIMIT 5;")
    rows = cursor.fetchall()
    print("Sample rows:")
    for row in rows:
        print(row)
    conn.close()
