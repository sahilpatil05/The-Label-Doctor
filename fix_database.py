"""
Fix database by deleting old schema and recreating with new structure
"""
import os
import json
from datetime import datetime

# Import the app and models
from app_api import app, db, Product, User

def fix_database():
    """Delete old database and recreate with new schema"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'labeldoctor.db')
    
    # Remove old database if it exists
    if os.path.exists(db_path):
        print(f"[INIT] Removing old database: {db_path}")
        try:
            os.remove(db_path)
            print(f"[SUCCESS] Database file removed")
        except PermissionError:
            print(f"[WARNING] Could not delete database (file in use). Will recreate with new schema.")
            print(f"[INFO] Attempting to rename instead...")
            import time
            backup_path = db_path + '.bak.' + str(int(time.time()))
            try:
                os.rename(db_path, backup_path)
                print(f"[SUCCESS] Database backed up to {backup_path}")
            except:
                print(f"[WARNING] Could not backup database either. Continuing anyway...")
    else:
        print(f"[INFO] No existing database found at {db_path}")
    
    # Create new database with current schema
    print("[INIT] Creating new database with fresh schema...")
    with app.app_context():
        db.create_all()
        print("[SUCCESS] Database tables created successfully")
        
        # Verify tables
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"[SUCCESS] Tables created: {tables}")
        
        # Check Product table columns
        if 'products' in tables:
            columns = [col['name'] for col in inspector.get_columns('products')]
            print(f"[INFO] Product table columns: {columns}")
            
            # Verify new schema
            if 'product_name' in columns and 'brand' in columns:
                print("[SUCCESS] Product table has correct schema with 'product_name' and 'brand'")
            else:
                print("[WARNING] Product table missing expected columns!")
    
    print("\n[SUCCESS] Database fix completed!")
    print("[NEXT] Run populate_food_products.py to load product data")

if __name__ == '__main__':
    fix_database()
