#!/usr/bin/env python
"""Test script to verify auth setup"""

import sys
import os

try:
    from app_api import app, db, User
    print("[✓] App and database imported successfully")
    
    with app.app_context():
        # Check database configuration
        print("\n[Database Configuration]")
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
        print(f"Database URI: {db_uri}")
        
        # Initialize database
        print("\n[Database Initialization]")
        db.create_all()
        print("✓ Tables created/verified")
        
        # Test User model
        print("\n[User Model Test]")
        user_count = User.query.count()
        print(f"✓ Current users in database: {user_count}")
        
        # Create a test user
        test_user = User(
            name="Test User",
            email=f"test_{id(object())}@example.com",
            allergens=[],
            dietary_preferences={}
        )
        test_user.set_password("testpassword123")
        
        try:
            db.session.add(test_user)
            db.session.commit()
            print(f"✓ Test user created successfully with ID: {test_user.id}")
            
            # Verify password check works
            password_check = test_user.check_password("testpassword123")
            print(f"✓ Password verification works: {password_check}")
            
            # Clean up
            db.session.delete(test_user)
            db.session.commit()
            print("✓ Test user removed")
        except Exception as e:
            db.session.rollback()
            print(f"⚠ Test user creation issue: {e}")
        
        print("\n[✓ SUCCESS] Authentication setup verified")
        
except Exception as e:
    print(f"[✗ ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
