# Product Allergen Database - API Documentation

## Overview
The new Product Allergen Database provides comprehensive allergen information and alternative product recommendations for packaged food items across 9 snack categories.

**Database Statistics:**
- Total Products: 136
- Categories: 9
- Brands: 25+
- Allergen-Free Products: 44
- Products with Allergens: 92

## Allergen Coverage
- Gluten: 57 products (41.9%)
- Milk: 42 products (30.9%)
- Tree Nuts: 21 products (15.4%)
- Peanuts: 5 products (3.7%)
- Egg: 1 product (0.7%)

## Product Categories
1. **Chips** - 26 products
2. **Extruded Snacks** - 7 products
3. **Namkeen** - 16 products
4. **Biscuits** - 18 products
5. **Crackers** - 3 products
6. **Chocolate** - 19 products
7. **Instant Noodles** - 18 products
8. **Snack Bars** - 12 products
9. **Nuts & Seeds** - 17 products

## API Endpoints (V2)

### 1. Get All Products
**Endpoint:** `GET /api/v2/products`

**Query Parameters:**
- `category` (optional): Filter by category
- `brand` (optional): Filter by brand
- `allergen_free` (optional): true/false - get only allergen-free products
- `limit` (optional, default=50): Number of products per page
- `page` (optional, default=1): Page number

**Example Request:**
```
GET /api/v2/products?category=Chips&allergen_free=true&limit=10
```

**Response:**
```json
{
  "success": true,
  "products": [
    {
      "id": "uuid",
      "brand": "Lay's",
      "product_name": "Classic Salted Chips",
      "category": "Chips",
      "ingredients": ["Potatoes", "Vegetable Oil", "Salt"],
      "allergens": [],
      "allergen_free": true,
      "possible_cross_contamination": [],
      "healthier_alternative_products": [],
      "rating": 4.2,
      "health_score": 35,
      "price": 2.49,
      "is_organic": false
    }
  ],
  "count": 10,
  "total": 100,
  "page": 1,
  "limit": 10,
  "pages": 10
}
```

---

### 2. Get Product by ID
**Endpoint:** `GET /api/v2/products/<product_id>`

**Example Request:**
```
GET /api/v2/products/abc123-def456
```

**Response:**
```json
{
  "success": true,
  "product": {
    "id": "abc123-def456",
    "brand": "Lay's",
    "product_name": "Cream & Onion Chips",
    "category": "Chips",
    "ingredients": ["Potatoes", "Vegetable Oil", "Milk Powder", "Salt"],
    "allergens": ["Milk"],
    "allergen_free": false,
    "possible_cross_contamination": ["Gluten"],
    "healthier_alternative_products": [
      "Lay's Classic Salted Chips",
      "Bingo! Plain Chips",
      "Pringles Original"
    ],
    "rating": 4.0,
    "health_score": 38,
    "price": 2.99,
    "is_organic": false
  }
}
```

---

### 3. Search Products
**Endpoint:** `GET /api/v2/products/search`

**Query Parameters:**
- `q` (required): Search keyword
- `category` (optional): Filter by category
- `limit` (optional, default=20): Maximum results

**Example Request:**
```
GET /api/v2/products/search?q=Lay's&category=Chips
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": "uuid",
      "brand": "Lay's",
      "product_name": "Classic Salted Chips",
      "category": "Chips",
      "allergens": [],
      "allergen_free": true
    }
  ],
  "count": 5
}
```

---

### 4. Get Products by Allergen (Find Safe Products)
**Endpoint:** `POST /api/v2/products/by-allergen`

**Request Body:**
```json
{
  "allergenic_items": ["Milk", "Gluten"],
  "category": "Biscuits",
  "limit": 20
}
```

**Response:**
```json
{
  "success": true,
  "safe_products": [
    {
      "id": "uuid",
      "brand": "Parle-G",
      "product_name": "Marie Biscuit",
      "category": "Biscuits",
      "allergens": ["Gluten"],
      "allergen_free": false,
      "rating": 4.1,
      "health_score": 43
    }
  ],
  "count": 8,
  "allergens_avoided": ["Milk", "Gluten"]
}
```

---

### 5. Get Alternative Products
**Endpoint:** `GET /api/v2/products/alternatives/<product_id>`

**Description:** Get healthier or allergen-free alternative products for a given product.

**Example Request:**
```
GET /api/v2/products/alternatives/abc123-def456
```

**Response:**
```json
{
  "success": true,
  "original_product": {
    "brand": "Lay's",
    "product_name": "Cream & Onion Chips",
    "allergens": ["Milk"]
  },
  "alternatives": [
    {
      "id": "xyz789",
      "brand": "Lay's",
      "product_name": "Classic Salted Chips",
      "category": "Chips",
      "allergens": [],
      "allergen_free": true,
      "rating": 4.2,
      "health_score": 35
    }
  ],
  "count": 3
}
```

---

### 6. Get All Categories
**Endpoint:** `GET /api/v2/categories`

**Response:**
```json
{
  "success": true,
  "categories": [
    "Biscuits",
    "Chips",
    "Chocolate",
    "Crackers",
    "Extruded Snacks",
    "Instant Noodles",
    "Namkeen",
    "Nuts & Seeds",
    "Snack Bars"
  ],
  "stats": {
    "Biscuits": 18,
    "Chips": 26,
    "Chocolate": 19,
    "Crackers": 3,
    "Extruded Snacks": 7,
    "Instant Noodles": 18,
    "Namkeen": 16,
    "Nuts & Seeds": 17,
    "Snack Bars": 12
  }
}
```

---

### 7. Get All Brands
**Endpoint:** `GET /api/v2/brands`

**Response:**
```json
{
  "success": true,
  "brands": [
    "Amul",
    "Bikaji",
    "Bingo!",
    "Boost",
    "Britannia",
    "Cadbury",
    "Haldiram's",
    "Happilo",
    "KitKat",
    "Kurkure",
    "Lay's",
    "Maggi",
    "Oreo",
    "Parle-G",
    "Pringles",
    "Yippee!"
  ],
  "stats": {
    "Lay's": 11,
    "Cadbury": 12,
    "Haldiram's": 10,
    "Bikaji": 9,
    "Kurkure": 9,
    "Maggi": 8
  }
}
```

---

### 8. Get All Allergens
**Endpoint:** `GET /api/v2/allergens`

**Response:**
```json
{
  "success": true,
  "allergens": [
    "Egg",
    "Gluten",
    "Milk",
    "Peanuts",
    "Sesame",
    "Soy",
    "Tree Nuts"
  ],
  "stats": {
    "Gluten": 57,
    "Milk": 42,
    "Tree Nuts": 21,
    "Peanuts": 5,
    "Egg": 1,
    "Sesame": 0,
    "Soy": 0
  },
  "total_unique": 7
}
```

---

### 9. Get Product Database Statistics
**Endpoint:** `GET /api/v2/products/stats`

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_products": 136,
    "allergen_free": 44,
    "organic": 0,
    "categories": 9,
    "brands": 25,
    "by_category": {
      "Biscuits": 18,
      "Chips": 26,
      "Chocolate": 19,
      "Crackers": 3,
      "Extruded Snacks": 7,
      "Instant Noodles": 18,
      "Namkeen": 16,
      "Nuts & Seeds": 17,
      "Snack Bars": 12
    },
    "by_brand": {
      "Lay's": 11,
      "Cadbury": 12,
      "Haldiram's": 10
    }
  }
}
```

---

## Data Structure

### Product Object
```json
{
  "id": "string (UUID)",
  "brand": "string",
  "product_name": "string",
  "category": "string",
  "ingredients": ["array of strings"],
  "allergens": ["array of allergen names"],
  "allergen_free": "boolean",
  "possible_cross_contamination": ["array of strings"],
  "healthier_alternative_products": ["array of product names"],
  "rating": "float (0-5)",
  "health_score": "float (0-100)",
  "price": "float",
  "is_organic": "boolean"
}
```

---

## Allergens Covered
- **Milk** - Dairy product allergen
- **Gluten** - Wheat and grain allergen
- **Soy** - Soy-based products
- **Peanuts** - Legume allergen
- **Tree Nuts** - Almonds, cashews, walnuts, etc.
- **Egg** - Egg products
- **Sesame** - Sesame seeds and oil
- **Mustard** - Mustard seeds and powder

---

## Features

### 1. Alternative Product Recommendations
When a product contains allergens, the database provides at least 3 healthier alternative products from the same or similar categories that do NOT contain those allergens.

### 2. Cross-Contamination Warnings
Products include information about possible cross-contamination risks, even if the allergen is not a direct ingredient.

### 3. Ingredient Transparency
Complete ingredient lists for every product enable detailed allergen analysis.

### 4. Health Scoring
Products are scored on health metrics (0-100) based on their nutritional profile and ingredient quality.

### 5. Category-Based Filtering
Find safe alternatives within the same snack category or across the entire database.

---

## Use Cases

### Case 1: Find Safe Alternative for a Product
```
1. GET /api/v2/products/search?q=Lay's%20Cream%20Onion
2. GET /api/v2/products/<id>/alternatives
3. Display healthier alternatives without Milk allergen
```

### Case 2: Find Allergen-Free Products in a Category
```
1. POST /api/v2/products/by-allergen
   {
     "allergenic_items": ["Milk", "Gluten"],
     "category": "Chips"
   }
2. Display all allergen-free chips
```

### Case 3: Build Allergen Profile
```
1. GET /api/v2/allergens
2. Display all available allergens
3. Allow user to select allergens to avoid
```

### Case 4: Product Comparison
```
1. GET /api/v2/products/<id1>
2. GET /api/v2/products/<id2>
3. Compare ingredients, allergens, health scores
```

---

## Error Handling

All endpoints return a standardized error response:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200 OK` - Request successful
- `400 Bad Request` - Invalid parameters or request body
- `404 Not Found` - Product or resource not found
- `500 Internal Server Error` - Server error

---

## Performance Notes

- Pagination is enforced on `/api/v2/products` (default limit: 50)
- Search results are limited to 20 by default
- Filter by category/brand for faster queries
- Use caching on the frontend for frequently accessed categories

---

## Integration Guide

### Frontend Implementation
```javascript
// Get safe products for user with specific allergies
const getUserAlternatives = async (allergies, category) => {
  const response = await fetch('/api/v2/products/by-allergen', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      allergenic_items: allergies,
      category: category,
      limit: 20
    })
  });
  return await response.json();
};
```

---

## Database Maintenance

To update the product database:

1. **Edit** `packaged_food_products.json` with new products
2. **Run** `python migrate_database.py` to update schema
3. **Run** `python populate_food_products.py` to load products
4. **Verify** with `GET /api/v2/products/stats`

---

*Last Updated: 2026-04-04*
*Version: 2.0 - With Comprehensive Allergen Support*
