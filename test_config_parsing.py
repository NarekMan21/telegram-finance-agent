#!/usr/bin/env python3
"""
Test for config-based transaction type determination with real config file
"""

import json
import sys
import os

# Add the project directory to the path so we can import telegram_parser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_parser import TelegramFinancialParser

def test_with_real_config():
    """Test that transaction types are determined by group ID using real config"""
    
    # Create parser instance with real config
    parser = TelegramFinancialParser('config.json')
    
    # Get group types from config
    group_types = parser.config.get('group_types', {})
    
    print("Testing with real config file...")
    print(f"Configured group types: {group_types}")
    
    # Test cases with real group IDs from config
    test_cases = [
        # (message, group_id, expected_type)
        ("Получил зарплату 50000 руб", "-4884869527", "income"),
        ("Купил продукты на 1500 руб", "-4855539306", "expense"),
    ]
    
    for message, group_id, expected_type in test_cases:
        result = parser.parse_financial_message(message, group_id)
        
        if result and result['type'] == expected_type:
            print(f"✓ Correctly identified {expected_type} for group {group_id}: {message}")
        else:
            print(f"✗ Failed to identify {expected_type} for group {group_id}: {message}")
            if result:
                print(f"  Got type: {result['type']}")
            else:
                print(f"  No transaction detected")
    
    # Test with unknown group
    unknown_result = parser.parse_financial_message("Сообщение 1000 руб", "-1001111111111")
    if unknown_result is None:
        print("✓ Correctly ignored message from unknown group")
    else:
        print(f"✗ Should have ignored message from unknown group, but got: {unknown_result}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_with_real_config()