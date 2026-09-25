import sqlite3
import os

db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION;")
        
        # 1. Rename old table
        cursor.execute('ALTER TABLE "cart_cart" RENAME TO "cart_cart_old";')
        
        # 2. Create new clean table matching Django expected schema
        cursor.execute('''
            CREATE TABLE "cart_cart" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
                "session_key" varchar(40) NULL, 
                "is_active" bool NOT NULL, 
                "created_at" datetime NOT NULL, 
                "updated_at" datetime NOT NULL, 
                "user_id" bigint NULL REFERENCES "accounts_customuser" ("id") DEFERRABLE INITIALLY DEFERRED
            );
        ''')
        
        # 3. Copy data from old table
        cursor.execute('''
            INSERT INTO "cart_cart" ("id", "session_key", "is_active", "created_at", "updated_at", "user_id")
            SELECT "id", "session_key", "is_active", "created_at", "updated_at", "user_id" 
            FROM "cart_cart_old";
        ''')
        
        # 4. Re-create indexes
        cursor.execute('CREATE INDEX "cart_cart_user_id_b645f9_idx" ON "cart_cart" ("user_id");')
        cursor.execute('CREATE INDEX "cart_cart_session_5e1af5_idx" ON "cart_cart" ("session_key");')
        cursor.execute('CREATE INDEX "cart_cart_user_id_9b4220b9" ON "cart_cart" ("user_id");')
        
        # 5. Drop old table
        cursor.execute('DROP TABLE "cart_cart_old";')
        
        conn.commit()
        print("Successfully rebuilt cart_cart table and removed legacy columns!")
    except Exception as e:
        conn.rollback()
        print(f"Error during migration rebuild: {e}")
    finally:
        conn.close()
else:
    print("Database file not found")
