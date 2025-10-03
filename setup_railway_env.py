#!/usr/bin/env python3
"""
Script to help set up Railway environment variables
"""

import json
import os

def generate_railway_env_instructions():
    """Generate instructions for setting up Railway environment variables"""
    
    print("=== Railway Environment Variables Setup ===")
    print()
    
    print("Please set the following environment variables in your Railway project:")
    print()
    
    print("1. API_ID (required)")
    print("   Your Telegram API ID from https://my.telegram.org")
    print("   Example: 12345678")
    print()
    
    print("2. API_HASH (required)")
    print("   Your Telegram API Hash from https://my.telegram.org")
    print("   Example: abcdef1234567890abcdef1234567890")
    print()
    
    print("3. PHONE_NUMBER (required)")
    print("   Your phone number registered with Telegram")
    print("   Example: +79281234567")
    print()
    
    print("4. GROUP_IDS (optional)")
    print("   Comma-separated list of group IDs or JSON array")
    print("   Example: -1001234567890,-1000987654321")
    print("   Or JSON: [\"-1001234567890\", \"-1000987654321\"]")
    print()
    
    print("5. GROUP_TYPES (optional)")
    print("   JSON object mapping group IDs to transaction types")
    print("   Example: {\"-1001234567890\": \"income\", \"-1000987654321\": \"expense\"}")
    print()
    
    print("6. CURRENCY (optional, default: RUB)")
    print("   Currency code")
    print("   Example: USD, EUR, RUB")
    print()
    
    print("7. NOTIFICATIONS (optional, default: true)")
    print("   Enable notifications")
    print("   Example: true or false")
    print()
    
    print("8. AUTO_UPDATE (optional, default: true)")
    print("   Enable auto update")
    print("   Example: true or false")
    print()
    
    print("9. UPDATE_INTERVAL (optional, default: 30)")
    print("   Update interval in seconds")
    print("   Example: 60")
    print()
    
    print("=== How to set environment variables in Railway ===")
    print()
    print("1. Go to your Railway project dashboard")
    print("2. Click on your service")
    print("3. Go to the 'Variables' tab")
    print("4. Click 'Add Variable' for each variable above")
    print("5. After setting all variables, redeploy your application")
    print()

def main():
    """Main function"""
    generate_railway_env_instructions()
    
    # Check if we're in a Railway environment
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("Detected Railway environment")
    else:
        print("Not running in Railway environment")
    
    # Generate example config
    example_config = {
        "API_ID": "YOUR_TELEGRAM_API_ID",
        "API_HASH": "YOUR_TELEGRAM_API_HASH",
        "PHONE_NUMBER": "+79281234567",
        "GROUP_IDS": ["-1001234567890", "-1000987654321"],
        "GROUP_TYPES": {
            "-1001234567890": "income",
            "-1000987654321": "expense"
        },
        "CURRENCY": "RUB",
        "NOTIFICATIONS": True,
        "AUTO_UPDATE": True,
        "UPDATE_INTERVAL": 30
    }
    
    print("=== Example Environment Variables JSON ===")
    print(json.dumps(example_config, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()