"""
Database migration script to update Product model schema.
This drops and recreates the products table with the new structure.
"""

from app_api import app, db, Product

def migrate_database():
    """Migrate database to new schema"""
    with app.app_context():
        print("🔄 Starting database migration...\n")
        
        # Drop existing products table
        print("📋 Dropping old 'products' table...")
        try:
            db.drop_all()
            print("✓ Old tables dropped successfully")
        except Exception as e:
            print(f"⚠ Error dropping tables: {e}")
        
        # Create new tables with updated schema
        print("\n📋 Creating new 'products' table with updated schema...")
        try:
            db.create_all()
            print("✓ New tables created successfully")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
        
        print("\n✅ Database migration complete!")
        print("\nNew Product schema includes:")
        print("  • brand")
        print("  • product_name")
        print("  • category")
        print("  • ingredients (JSON list)")
        print("  • allergens (JSON list)")
        print("  • allergen_free (boolean)")
        print("  • possible_cross_contamination (JSON list)")
        print("  • healthier_alternative_products (JSON list)")
        print("  • rating")
        print("  • health_score")
        print("  • price")
        print("  • is_organic")
        
        return True

if __name__ == '__main__':
    print("\n" + "="*70)
    print("DATABASE MIGRATION - PRODUCT MODEL UPDATE")
    print("="*70 + "\n")
    
    success = migrate_database()
    
    if success:
        print("\n" + "="*70)
        print("Run 'python populate_food_products.py' to populate the database")
        print("="*70 + "\n")
