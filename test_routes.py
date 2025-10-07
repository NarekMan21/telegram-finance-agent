#!/usr/bin/env python3
"""
Test script to check Flask routes
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_routes():
    """Test Flask routes"""
    print("Testing Flask routes...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test settings routes
            print("\nTesting /settings route...")
            response = client.get('/settings')
            print(f"Status code: {response.status_code}")
            print(f"Content type: {response.content_type}")
            if response.status_code == 200:
                print("✓ /settings route works")
            else:
                print(f"✗ /settings route failed with status {response.status_code}")
                print(f"Response: {response.get_data(as_text=True)[:200]}...")
            
            print("\nTesting /settings.html route...")
            response = client.get('/settings.html')
            print(f"Status code: {response.status_code}")
            print(f"Content type: {response.content_type}")
            if response.status_code == 200:
                print("✓ /settings.html route works")
            else:
                print(f"✗ /settings.html route failed with status {response.status_code}")
                print(f"Response: {response.get_data(as_text=True)[:200]}...")
                
            # Test other routes
            print("\nTesting / route...")
            response = client.get('/')
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                print("✓ / route works")
            else:
                print(f"✗ / route failed with status {response.status_code}")
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_routes()