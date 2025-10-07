#!/usr/bin/env python3
"""
Test script to check if settings page loads correctly
"""

import os
import sys
from flask import Flask, render_template

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_settings_page():
    """Test if settings page template can be loaded"""
    print("Testing settings page loading...")
    
    # Create a test Flask app
    app = Flask(__name__, template_folder='templates')
    
    try:
        # Check if template directory exists
        template_dir = app.template_folder or 'templates'
        print(f"Template directory: {template_dir}")
        
        if not os.path.exists(str(template_dir)):
            print(f"ERROR: Template directory does not exist: {template_dir}")
            return False
            
        # Check if settings.html exists
        settings_template = os.path.join(str(template_dir), 'settings.html')
        print(f"Checking for settings template: {settings_template}")
        
        if not os.path.exists(settings_template):
            print(f"ERROR: Settings template does not exist: {settings_template}")
            # List all files in template directory
            print("Files in template directory:")
            for file in os.listdir(str(template_dir)):
                print(f"  - {file}")
            return False
            
        print("SUCCESS: Settings template found")
        
        # Try to load the template
        with app.app_context():
            try:
                rendered = render_template('settings.html')
                print("SUCCESS: Settings template rendered successfully")
                print(f"Template size: {len(rendered)} characters")
                return True
            except Exception as e:
                print(f"ERROR: Failed to render settings template: {e}")
                return False
                
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_settings_page()
    if success:
        print("\n✓ Settings page test PASSED")
    else:
        print("\n✗ Settings page test FAILED")
        sys.exit(1)