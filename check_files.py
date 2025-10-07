#!/usr/bin/env python3
"""
Simple test to verify web files exist
"""

import os

def check_files():
    """Check if required web files exist"""
    required_files = [
        'index.html',
        'main.js',
        'analytics.html',
        'settings.html',
        'transactions.html'
    ]
    
    print("Checking for required web files:")
    print("-" * 40)
    
    all_found = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing")
            all_found = False
    
    # Check templates directory
    if os.path.exists('templates') and os.path.isdir('templates'):
        templates = os.listdir('templates')
        print(f"📁 templates/ - Found ({len(templates)} files)")
        for template in templates:
            print(f"  - {template}")
    else:
        print("❌ templates/ - Missing")
        all_found = False
    
    return all_found

if __name__ == '__main__':
    print("📂 Telegram Financial Agent - File Check")
    print("=" * 50)
    
    success = check_files()
    
    if success:
        print("\n🎉 All required files are present!")
    else:
        print("\n⚠️  Some files are missing.")