"""
Populate database with comprehensive packaged food products dataset.
Supports allergen detection and alternative product recommendations.
"""

import json
from app_api import app, db, Product
import uuid

def load_product_data(filename='packaged_food_products.json'):
    """Load product data from JSON file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data.get('products', [])
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return []

def populate_products():
    """Populate database with food products"""
    products_data = load_product_data()
    
    if not products_data:
        print("No products to populate.")
        return
    
    with app.app_context():
        # Clear existing products (optional - comment out to preserve existing data)
        # Product.query.delete()
        
        count = 0
        skipped = 0
        
        for product_data in products_data:
            # Check if product already exists
            existing = Product.query.filter_by(
                brand=product_data.get('brand'),
                product_name=product_data.get('product_name')
            ).first()
            
            if existing:
                print(f"⚠ Skipped: {product_data['brand']} - {product_data['product_name']} (already exists)")
                skipped += 1
                continue
            
            # Create new product
            product = Product(
                id=str(uuid.uuid4()),
                brand=product_data.get('brand', 'Unknown'),
                product_name=product_data.get('product_name', 'Unknown'),
                category=product_data.get('category', 'General'),
                ingredients=product_data.get('ingredients', []),
                allergens=product_data.get('allergens', []),
                allergen_free=product_data.get('allergen_free', True),
                possible_cross_contamination=product_data.get('possible_cross_contamination', []),
                healthier_alternative_products=product_data.get('healthier_alternative_products', []),
                rating=product_data.get('rating', 0.0),
                health_score=product_data.get('health_score', 0.0),
                price=product_data.get('price', 0.0),
                is_organic=product_data.get('is_organic', False)
            )
            
            db.session.add(product)
            count += 1
            print(f"✓ Added: {product_data['brand']} - {product_data['product_name']} ({product_data['category']})")
        
        db.session.commit()
        
        total_products = Product.query.count()
        print(f"\n{'='*70}")
        print(f"✅ Successfully added {count} new products to database!")
        print(f"⚠ Skipped {skipped} duplicate products")
        print(f"📊 Total products in database: {total_products}")
        print(f"{'='*70}\n")
        
        # Print category summary
        categories = db.session.query(Product.category).distinct().all()
        print("📋 Products by Category:")
        for category in sorted([cat[0] for cat in categories]):
            cat_count = Product.query.filter_by(category=category).count()
            print(f"  • {category}: {cat_count} products")
        
        # Print brand summary
        brands = db.session.query(Product.brand).distinct().all()
        print(f"\n🏷️ Products by Brand:")
        for brand in sorted([b[0] for b in brands]):
            brand_count = Product.query.filter_by(brand=brand).count()
            print(f"  • {brand}: {brand_count} products")

def get_allergen_statistics():
    """Print allergen statistics"""
    with app.app_context():
        all_products = Product.query.all()
        
        allergen_counts = {}
        allergen_free_count = 0
        
        for product in all_products:
            if product.allergen_free:
                allergen_free_count += 1
            else:
                for allergen in product.allergens:
                    allergen_counts[allergen] = allergen_counts.get(allergen, 0) + 1
        
        print(f"\n{'='*70}")
        print("🔍 ALLERGEN STATISTICS")
        print(f"{'='*70}")
        print(f"Total Products: {len(all_products)}")
        print(f"Allergen-Free Products: {allergen_free_count}")
        print(f"Products with Allergens: {len(all_products) - allergen_free_count}")
        
        print(f"\nMost Common Allergens:")
        for allergen, count in sorted(allergen_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(all_products)) * 100
            print(f"  • {allergen}: {count} products ({percentage:.1f}%)")
        print(f"{'='*70}\n")

if __name__ == '__main__':
    print("\n" + "="*70)
    print("POPULATING DATABASE WITH PACKAGED FOOD PRODUCTS")
    print("="*70 + "\n")
    
    populate_products()
    get_allergen_statistics()
    
    print("✨ Database population complete!")
