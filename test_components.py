#!/usr/bin/env python3
"""
Test script to verify Telegram Financial Agent components
"""

import sys
import os
import json

def test_config():
    """Test if config file exists and is valid"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ Config file loaded successfully")
        print(f"   API ID: {config.get('api_id')}")
        print(f"   Phone number: {config.get('phone_number')}")
        print(f"   Group IDs: {config.get('group_ids')}")
        return True
    except FileNotFoundError:
        print("❌ Config file not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False

def test_imports():
    """Test if required modules can be imported"""
    modules = ['flask', 'telethon', 'pandas', 'numpy']
    success = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            success = False
    
    return success

def main():
    print("🧪 Testing Telegram Financial Agent components...")
    print("=" * 50)
    
    config_ok = test_config()
    imports_ok = test_imports()
    
    if config_ok and imports_ok:
        print("\n🎉 All tests passed! You can run the application.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())