#!/usr/bin/env python
from app_api import app

# Test the app routes directly
with app.test_client() as client:
    print("Testing /api/v2/categories...")
    response = client.get('/api/v2/categories')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    print("\nTesting /api/v2/products...")
    response = client.get('/api/v2/products')
    print(f"Status: {response.status_code}")
    data = response.get_json()
    if data.get('success'):
        print(f"Products count: {data.get('count')}")
    else:
        print(f"Response: {data}")
    
    print("\nTesting /api/v2/brands...")
    response = client.get('/api/v2/brands')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
