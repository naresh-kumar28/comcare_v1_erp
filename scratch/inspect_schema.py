import sqlite3
import os

db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT type, name, tbl_name, sql FROM sqlite_master;")
    items = cursor.fetchall()
    print("Database Schema Items:")
    for item in items:
        if 'cart_cart' in item[2] or 'cart_cart_old' in str(item[3]):
            print(f"Type: {item[0]}, Name: {item[1]}, Table: {item[2]}")
            print(f"SQL: {item[3]}")
            print("-" * 50)
    conn.close()
else:
    print("Database file not found")
