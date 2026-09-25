import sqlite3
import os

db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION;")
        
        # 0. Drop indexes on old table if they exist
        cursor.execute('DROP INDEX IF EXISTS "cart_cartitem_cart_id_product_id_53cce7c3_uniq";')
        cursor.execute('DROP INDEX IF EXISTS "cart_cartitem_cart_id_370ad265";')
        cursor.execute('DROP INDEX IF EXISTS "cart_cartitem_product_id_b24e265a";')
        
        # 1. Rename old table
        cursor.execute('ALTER TABLE "cart_cartitem" RENAME TO "cart_cartitem_old";')
        
        # 2. Create new clean table referencing correct cart_cart table name
        cursor.execute('''
            CREATE TABLE "cart_cartitem" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
                "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), 
                "unit_price" decimal NULL, 
                "added_at" datetime NOT NULL, 
                "updated_at" datetime NOT NULL, 
                "cart_id" bigint NOT NULL REFERENCES "cart_cart" ("id") DEFERRABLE INITIALLY DEFERRED, 
                "product_id" bigint NOT NULL REFERENCES "store_product" ("id") DEFERRABLE INITIALLY DEFERRED,
                "is_active" bool NOT NULL
            );
        ''')
        
        # 3. Copy data from old table
        cursor.execute('''
            INSERT INTO "cart_cartitem" ("id", "quantity", "unit_price", "added_at", "updated_at", "cart_id", "product_id", "is_active")
            SELECT "id", "quantity", "unit_price", "added_at", "updated_at", "cart_id", "product_id", "is_active" 
            FROM "cart_cartitem_old";
        ''')
        
        # 4. Re-create indexes
        cursor.execute('CREATE UNIQUE INDEX "cart_cartitem_cart_id_product_id_53cce7c3_uniq" ON "cart_cartitem" ("cart_id", "product_id");')
        cursor.execute('CREATE INDEX "cart_cartitem_cart_id_370ad265" ON "cart_cartitem" ("cart_id");')
        cursor.execute('CREATE INDEX "cart_cartitem_product_id_b24e265a" ON "cart_cartitem" ("product_id");')
        
        # 5. Drop old table
        cursor.execute('DROP TABLE "cart_cartitem_old";')
        
        conn.commit()
        print("Successfully rebuilt cart_cartitem table and fixed foreign key reference to cart_cart!")
    except Exception as e:
        conn.rollback()
        print(f"Error during cartitem rebuild: {e}")
    finally:
        conn.close()
else:
    print("Database file not found")
