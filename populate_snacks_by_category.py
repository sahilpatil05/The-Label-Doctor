"""
Populate database with comprehensive food snacks organized by category.
This enables category-based alternative recommendations.
"""

from app_api import app, db, Product
import uuid

# Comprehensive food snacks database organized by category
FOOD_SNACKS_BY_CATEGORY = {
    'Chips & Crisps': [
        {
            'name': 'Potato Chips',
            'brand': 'Lay\'s',
            'allergens_free': ['dairy', 'egg', 'gluten'],
            'rating': 4.2,
            'health_score': 35,
            'price': 2.49,
            'is_organic': False,
            'ingredients': ['potatoes', 'vegetable oil', 'salt']
        },
        {
            'name': 'Tortilla Chips',
            'brand': 'Tostitos',
            'allergens_free': ['dairy', 'tree_nut', 'egg'],
            'rating': 4.1,
            'health_score': 40,
            'price': 2.99,
            'is_organic': False,
            'ingredients': ['corn', 'vegetable oil', 'salt']
        },
        {
            'name': 'Banana Chips',
            'brand': 'Tropicals',
            'allergens_free': ['dairy', 'gluten', 'peanut', 'shellfish', 'egg'],
            'rating': 4.0,
            'health_score': 45,
            'price': 3.49,
            'is_organic': True,
            'ingredients': ['bananas', 'coconut oil', 'sea salt']
        },
        {
            'name': 'Tapioca Chips',
            'brand': 'Harvest Snaps',
            'allergens_free': ['dairy', 'gluten', 'peanut', 'tree_nut', 'egg'],
            'rating': 4.3,
            'health_score': 50,
            'price': 3.29,
            'is_organic': True,
            'ingredients': ['tapioca', 'pea starch', 'vegetable oil', 'salt']
        },
        {
            'name': 'Corn Chips',
            'brand': 'Fritos',
            'allergens_free': ['dairy', 'tree_nut', 'egg'],
            'rating': 4.0,
            'health_score': 38,
            'price': 2.79,
            'is_organic': False,
            'ingredients': ['corn', 'vegetable oil', 'salt']
        },
        {
            'name': 'Prawn Crackers',
            'brand': 'Lucky Me',
            'allergens_free': ['dairy', 'tree_nut'],
            'rating': 4.2,
            'health_score': 42,
            'price': 1.99,
            'is_organic': False,
            'ingredients': ['tapioca starch', 'prawn', 'salt', 'spices']
        }
    ],
    'Extruded Snacks': [
        {
            'name': 'Cheese Balls',
            'brand': 'Cheetos',
            'allergens_free': ['tree_nut', 'shellfish', 'egg'],
            'rating': 4.1,
            'health_score': 35,
            'price': 2.49,
            'is_organic': False,
            'ingredients': ['corn meal', 'cheese flavor', 'vegetable oil', 'salt']
        },
        {
            'name': 'Cheese Puffs',
            'brand': 'Doritos',
            'allergens_free': ['tree_nut', 'shellfish'],
            'rating': 4.2,
            'health_score': 38,
            'price': 2.99,
            'is_organic': False,
            'ingredients': ['corn', 'cheese', 'vegetable oil', 'salt']
        },
        {
            'name': 'Corn Rings',
            'brand': 'OnionRings',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 3.9,
            'health_score': 36,
            'price': 1.99,
            'is_organic': False,
            'ingredients': ['corn meal', 'vegetable oil', 'salt']
        },
        {
            'name': 'Corn Sticks',
            'brand': 'Funyuns',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish'],
            'rating': 4.0,
            'health_score': 37,
            'price': 2.29,
            'is_organic': False,
            'ingredients': ['corn meal', 'onion flavor', 'vegetable oil', 'salt']
        },
        {
            'name': 'Masala Sticks',
            'brand': 'RiteBite',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.3,
            'health_score': 40,
            'price': 2.49,
            'is_organic': False,
            'ingredients': ['corn', 'masala spice', 'vegetable oil', 'salt']
        }
    ],
    'Namkeen / Savory Mixes': [
        {
            'name': 'Bhujia',
            'brand': 'Bikano',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.4,
            'health_score': 45,
            'price': 3.49,
            'is_organic': False,
            'ingredients': ['gram flour', 'vegetable oil', 'spices', 'salt']
        },
        {
            'name': 'Sev',
            'brand': 'Haldiram\'s',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.3,
            'health_score': 43,
            'price': 2.99,
            'is_organic': False,
            'ingredients': ['gram flour', 'vegetable oil', 'chili powder', 'salt']
        },
        {
            'name': 'Chivda / Poha Mix',
            'brand': 'Bhakarwadi',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.2,
            'health_score': 48,
            'price': 3.99,
            'is_organic': True,
            'ingredients': ['poha', 'peanuts', 'cashews', 'spices', 'salt']
        },
        {
            'name': 'Bombay Mix',
            'brand': 'Mahendra',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.4,
            'health_score': 50,
            'price': 3.29,
            'is_organic': False,
            'ingredients': ['nuts mix', 'lentils', 'spices', 'vegetable oil']
        },
        {
            'name': 'Dal Moth',
            'brand': 'Aara',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.1,
            'health_score': 46,
            'price': 2.79,
            'is_organic': False,
            'ingredients': ['lentils', 'moong dal', 'vegetable oil', 'spices']
        },
        {
            'name': 'Roasted Chana Mix',
            'brand': 'ITC',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.5,
            'health_score': 55,
            'price': 3.49,
            'is_organic': True,
            'ingredients': ['roasted chickpeas', 'peanuts', 'corn', 'spices']
        }
    ],
    'Crackers & Biscuits': [
        {
            'name': 'Salted Crackers',
            'brand': 'Britannia',
            'allergens_free': ['tree_nut', 'shellfish', 'egg'],
            'rating': 4.0,
            'health_score': 42,
            'price': 1.99,
            'is_organic': False,
            'ingredients': ['wheat flour', 'vegetable oil', 'salt']
        },
        {
            'name': 'Cream Biscuits',
            'brand': 'Parle',
            'allergens_free': ['tree_nut', 'shellfish'],
            'rating': 4.2,
            'health_score': 40,
            'price': 2.49,
            'is_organic': False,
            'ingredients': ['wheat flour', 'cream', 'sugar', 'vegetable oil']
        },
        {
            'name': 'Digestive Biscuits',
            'brand': 'McVitie\'s',
            'allergens_free': ['tree_nut', 'shellfish'],
            'rating': 4.3,
            'health_score': 48,
            'price': 3.29,
            'is_organic': False,
            'ingredients': ['wheat flour', 'oats', 'sugar', 'vegetable oil']
        },
        {
            'name': 'Marie Biscuits',
            'brand': 'Sunfeast',
            'allergens_free': ['tree_nut', 'shellfish'],
            'rating': 4.1,
            'health_score': 43,
            'price': 2.29,
            'is_organic': False,
            'ingredients': ['wheat flour', 'sugar', 'vegetable oil', 'salt']
        },
        {
            'name': 'Cheese Crackers',
            'brand': 'Cheez-It',
            'allergens_free': ['tree_nut', 'shellfish'],
            'rating': 4.2,
            'health_score': 40,
            'price': 3.49,
            'is_organic': False,
            'ingredients': ['wheat flour', 'cheese', 'vegetable oil', 'salt']
        }
    ],
    'Baked Snacks': [
        {
            'name': 'Baked Chips',
            'brand': 'Baked Lay\'s',
            'allergens_free': ['dairy', 'egg'],
            'rating': 4.4,
            'health_score': 58,
            'price': 2.79,
            'is_organic': False,
            'ingredients': ['potatoes', 'corn starch', 'vegetable oil', 'salt']
        },
        {
            'name': 'Breadsticks',
            'brand': 'Grissini',
            'allergens_free': ['tree_nut', 'shellfish', 'dairy'],
            'rating': 4.1,
            'health_score': 50,
            'price': 2.49,
            'is_organic': True,
            'ingredients': ['wheat flour', 'water', 'salt', 'yeast']
        },
        {
            'name': 'Pretzels',
            'brand': 'Snyder\'s',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.2,
            'health_score': 48,
            'price': 3.29,
            'is_organic': False,
            'ingredients': ['wheat flour', 'vegetable oil', 'salt', 'water']
        },
        {
            'name': 'Rice Crackers',
            'brand': 'Riceworks',
            'allergens_free': ['dairy', 'gluten', 'peanut', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.3,
            'health_score': 52,
            'price': 3.49,
            'is_organic': True,
            'ingredients': ['brown rice', 'vegetable oil', 'sea salt']
        }
    ],
    'Nuts & Seed Snacks': [
        {
            'name': 'Roasted Peanuts',
            'brand': 'Planters',
            'allergens_free': ['dairy', 'gluten', 'shellfish', 'egg'],
            'rating': 4.5,
            'health_score': 62,
            'price': 3.99,
            'is_organic': False,
            'ingredients': ['peanuts', 'vegetable oil', 'salt']
        },
        {
            'name': 'Flavored Almonds',
            'brand': 'Wonderful',
            'allergens_free': ['dairy', 'gluten', 'shellfish', 'egg'],
            'rating': 4.6,
            'health_score': 70,
            'price': 4.99,
            'is_organic': True,
            'ingredients': ['almonds', 'sea salt', 'spices']
        },
        {
            'name': 'Cashews',
            'brand': 'Kamaraj',
            'allergens_free': ['dairy', 'gluten', 'peanut', 'shellfish', 'egg'],
            'rating': 4.7,
            'health_score': 72,
            'price': 5.99,
            'is_organic': True,
            'ingredients': ['cashews', 'sea salt']
        },
        {
            'name': 'Pistachios',
            'brand': 'Setton Farms',
            'allergens_free': ['dairy', 'gluten', 'peanut', 'shellfish', 'egg'],
            'rating': 4.8,
            'health_score': 75,
            'price': 6.49,
            'is_organic': True,
            'ingredients': ['pistachios', 'sea salt']
        },
        {
            'name': 'Sunflower Seeds',
            'brand': 'David\'s',
            'allergens_free': ['dairy', 'gluten', 'peanut', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.4,
            'health_score': 65,
            'price': 2.99,
            'is_organic': True,
            'ingredients': ['sunflower seeds', 'sea salt']
        },
        {
            'name': 'Pumpkin Seeds',
            'brand': 'Simply Balanced',
            'allergens_free': ['dairy', 'gluten', 'peanut', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.5,
            'health_score': 68,
            'price': 3.49,
            'is_organic': True,
            'ingredients': ['pumpkin seeds', 'sea salt']
        }
    ],
    'Sweet Snacks': [
        {
            'name': 'Chocolate Bars',
            'brand': 'Cadbury',
            'allergens_free': ['gluten', 'peanut', 'shellfish'],
            'rating': 4.5,
            'health_score': 45,
            'price': 1.99,
            'is_organic': False,
            'ingredients': ['cocoa', 'sugar', 'milk powder', 'vegetable oil']
        },
        {
            'name': 'Candy / Toffees',
            'brand': 'Bournvita',
            'allergens_free': ['gluten', 'peanut', 'shellfish'],
            'rating': 4.3,
            'health_score': 40,
            'price': 1.49,
            'is_organic': False,
            'ingredients': ['sugar', 'milk powder', 'cocoa', 'vegetable oil']
        },
        {
            'name': 'Gummies',
            'brand': 'Haribo',
            'allergens_free': ['gluten', 'peanut', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.2,
            'health_score': 35,
            'price': 2.49,
            'is_organic': False,
            'ingredients': ['gelatin', 'sugar', 'gum arabic', 'natural flavors']
        },
        {
            'name': 'Caramel Popcorn',
            'brand': 'Cracker Jack',
            'allergens_free': ['tree_nut', 'shellfish', 'egg'],
            'rating': 4.4,
            'health_score': 42,
            'price': 2.99,
            'is_organic': False,
            'ingredients': ['popcorn', 'caramel', 'peanuts', 'salt']
        },
        {
            'name': 'Sweet Wafers',
            'brand': 'Loacker',
            'allergens_free': ['peanut', 'shellfish'],
            'rating': 4.6,
            'health_score': 50,
            'price': 3.29,
            'is_organic': True,
            'ingredients': ['wheat flour', 'milk', 'hazelnut', 'honey']
        }
    ],
    'Snack Bars': [
        {
            'name': 'Granola Bars',
            'brand': 'Nature Valley',
            'allergens_free': ['shellfish', 'egg'],
            'rating': 4.5,
            'health_score': 68,
            'price': 3.49,
            'is_organic': True,
            'ingredients': ['oats', 'honey', 'almonds', 'coconut', 'cinnamon']
        },
        {
            'name': 'Protein Bars',
            'brand': 'Quest',
            'allergens_free': ['shellfish', 'dairy', 'gluten'],
            'rating': 4.6,
            'health_score': 75,
            'price': 2.99,
            'is_organic': False,
            'ingredients': ['whey protein', 'almonds', 'dark chocolate', 'monk fruit']
        },
        {
            'name': 'Energy Bars',
            'brand': 'Clif Bar',
            'allergens_free': ['shellfish', 'egg'],
            'rating': 4.4,
            'health_score': 72,
            'price': 1.99,
            'is_organic': True,
            'ingredients': ['oats', 'nuts', 'honey', 'date paste']
        },
        {
            'name': 'Fruit Bars',
            'brand': 'Larabar',
            'allergens_free': ['dairy', 'gluten', 'peanut', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.7,
            'health_score': 78,
            'price': 1.99,
            'is_organic': True,
            'ingredients': ['dates', 'almonds', 'sea salt']
        }
    ],
    'Instant / Ready-to-eat Foods': [
        {
            'name': 'Instant Noodles',
            'brand': 'Maggi',
            'allergens_free': ['tree_nut', 'shellfish'],
            'rating': 3.8,
            'health_score': 35,
            'price': 0.99,
            'is_organic': False,
            'ingredients': ['wheat noodles', 'vegetable oil', 'salt', 'spices']
        },
        {
            'name': 'Cup Noodles',
            'brand': 'Nissin',
            'allergens_free': ['tree_nut', 'shellfish'],
            'rating': 3.9,
            'health_score': 36,
            'price': 1.49,
            'is_organic': False,
            'ingredients': ['noodles', 'seasoning', 'dehydrated vegetables']
        },
        {
            'name': 'Instant Pasta',
            'brand': 'Knorr',
            'allergens_free': ['tree_nut', 'shellfish'],
            'rating': 3.7,
            'health_score': 38,
            'price': 1.99,
            'is_organic': False,
            'ingredients': ['pasta', 'seasoning mix', 'salt']
        },
        {
            'name': 'Ready-to-eat Soups',
            'brand': 'Campbell\'s',
            'allergens_free': ['tree_nut', 'shellfish', 'egg'],
            'rating': 4.0,
            'health_score': 40,
            'price': 2.29,
            'is_organic': False,
            'ingredients': ['vegetables', 'broth', 'salt', 'spices']
        }
    ],
    'Fried Snacks': [
        {
            'name': 'Samosa Chips',
            'brand': 'Balaji',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.3,
            'health_score': 38,
            'price': 2.49,
            'is_organic': False,
            'ingredients': ['potato', 'spices', 'vegetable oil', 'salt']
        },
        {
            'name': 'Papdi',
            'brand': 'Anil',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.2,
            'health_score': 40,
            'price': 3.99,
            'is_organic': False,
            'ingredients': ['wheat flour', 'oil', 'spices', 'salt']
        },
        {
            'name': 'Chakli / Murukku',
            'brand': 'Astra',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.1,
            'health_score': 42,
            'price': 2.99,
            'is_organic': False,
            'ingredients': ['rice flour', 'oil', 'chili powder', 'salt']
        },
        {
            'name': 'Mathri',
            'brand': 'Agro',
            'allergens_free': ['dairy', 'tree_nut', 'shellfish', 'egg'],
            'rating': 4.2,
            'health_score': 44,
            'price': 2.49,
            'is_organic': False,
            'ingredients': ['wheat flour', 'oil', 'carom seeds', 'salt']
        }
    ]
}

def populate_snacks():
    """Populate database with categorized food snacks"""
    with app.app_context():
        # Clear existing products (optional)
        # Product.query.delete()
        
        count = 0
        for category, snacks in FOOD_SNACKS_BY_CATEGORY.items():
            for snack in snacks:
                # Check if product already exists
                existing = Product.query.filter_by(name=snack['name'], brand=snack['brand']).first()
                if existing:
                    print(f"ℹ️ Product '{snack['name']}' already exists, skipping...")
                    continue
                
                product = Product(
                    id=str(uuid.uuid4()),
                    name=snack['name'],
                    brand=snack['brand'],
                    category=category,
                    allergen_free=snack['allergens_free'],
                    ingredients_list=snack['ingredients'],
                    rating=snack['rating'],
                    health_score=snack['health_score'],
                    price=snack['price'],
                    is_organic=snack['is_organic']
                )
                db.session.add(product)
                count += 1
                print(f"✓ Added: {snack['name']} ({category})")
        
        db.session.commit()
        print(f"\n✅ Successfully added {count} food products to database!")
        print(f"Categories: {', '.join(FOOD_SNACKS_BY_CATEGORY.keys())}")

if __name__ == '__main__':
    populate_snacks()
