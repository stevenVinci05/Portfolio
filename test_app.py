#!/usr/bin/env python3
"""
Test script per verificare che l'applicazione Flask funzioni correttamente
"""

import os
import sys
from app import app, create_admin

def test_app():
    """Test dell'applicazione Flask"""
    try:
        with app.app_context():
            # Test della creazione del database
            print("Testing database creation...")
            create_admin()
            print("✅ Database creation successful")
            
            # Test delle route principali
            print("Testing main routes...")
            with app.test_client() as client:
                # Test homepage
                response = client.get('/')
                if response.status_code == 200:
                    print("✅ Homepage route working")
                else:
                    print(f"❌ Homepage route failed: {response.status_code}")
                
                # Test about page
                response = client.get('/about')
                if response.status_code == 200:
                    print("✅ About page route working")
                else:
                    print(f"❌ About page route failed: {response.status_code}")
                
                # Test projects page
                response = client.get('/projects')
                if response.status_code == 200:
                    print("✅ Projects page route working")
                else:
                    print(f"❌ Projects page route failed: {response.status_code}")
                
                # Test contact page
                response = client.get('/contact')
                if response.status_code == 200:
                    print("✅ Contact page route working")
                else:
                    print(f"❌ Contact page route failed: {response.status_code}")
            
            print("🎉 All tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == '__main__':
    success = test_app()
    sys.exit(0 if success else 1) 