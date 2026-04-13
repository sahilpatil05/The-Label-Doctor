#!/usr/bin/env python
from app_api import app, db, Product
from sqlalchemy import inspect

app.app_context().push()

# Check tables
inspector = inspect(db.engine)
tables = inspector.get_table_names()
print(f"Tables in database: {tables}")
print(f"Products table exists: {'products' in tables}")

# Count products
try:
    count = Product.query.count()
    print(f"Total products: {count}")
    
    if count > 0:
        first_product = Product.query.first()
        print(f"\nFirst product:")
        print(f"  - Brand: {first_product.brand}")
        print(f"  - Name: {first_product.product_name}")
        print(f"  - Category: {first_product.category}")
        print(f"  - Allergens: {first_product.allergens}")
except Exception as e:
    print(f"Error querying products: {e}")
    import traceback
    traceback.print_exc()
