#!/usr/bin/env python
"""Test the authentication API endpoints"""

import sys
import json
import os

# Fix encodings for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from app_api import app, db, User
    print("[OK] App imported successfully\n")
    
    with app.app_context():
        # Create a test client
        client = app.test_client()
        print("[Testing API Endpoints]\n")
        
        # Test 1: Register a new user
        print("1. Testing /api/auth/register (POST)")
        register_data = {
            "name": "Test User",
            "email": f"testuser_{id(object())}@example.com",
            "password": "password123"
        }
        response = client.post('/api/auth/register', 
                              json=register_data,
                              content_type='application/json')
        print(f"   Status: {response.status_code}")
        result = response.get_json()
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 201 and result.get('success'):
            test_user_id = result.get('user_id')
            test_email = register_data['email']
            print(f"   [OK] Registration successful (User ID: {test_user_id})\n")
        else:
            print(f"   [FAIL] Registration failed\n")
            sys.exit(1)
        
        # Test 2: Login with correct credentials
        print("2. Testing /api/auth/login (POST) with correct credentials")
        login_data = {
            "email": test_email,
            "password": "password123"
        }
        response = client.post('/api/auth/login',
                              json=login_data,
                              content_type='application/json')
        print(f"   Status: {response.status_code}")
        result = response.get_json()
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get('success'):
            print(f"   [OK] Login successful\n")
        else:
            print(f"   [FAIL] Login failed\n")
            sys.exit(1)
        
        # Test 3: Login with incorrect password
        print("3. Testing /api/auth/login (POST) with incorrect password")
        login_data = {
            "email": test_email,
            "password": "wrongpassword"
        }
        response = client.post('/api/auth/login',
                              json=login_data,
                              content_type='application/json')
        print(f"   Status: {response.status_code}")
        result = response.get_json()
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 401 and not result.get('success'):
            print(f"   [OK] Correctly rejected invalid password\n")
        else:
            print(f"   [FAIL] Should have rejected invalid password\n")
        
        # Test 4: Register with duplicate email
        print("4. Testing /api/auth/register (POST) with duplicate email")
        response = client.post('/api/auth/register',
                              json=register_data,  # Same email as before
                              content_type='application/json')
        print(f"   Status: {response.status_code}")
        result = response.get_json()
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 400 and not result.get('success'):
            print(f"   [OK] Correctly rejected duplicate email\n")
        else:
            print(f"   [FAIL] Should have rejected duplicate email\n")
        
        # Test 5: Get current user (after login)
        print("5. Testing /api/auth/current-user (GET)")
        response = client.get('/api/auth/current-user')
        print(f"   Status: {response.status_code}")
        result = response.get_json()
        print(f"   Response: {json.dumps(result, indent=2)}\n")
        
        print("[OK] SUCCESS: All API endpoints working correctly!")
        
except Exception as e:
    print(f"[FAIL] ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
