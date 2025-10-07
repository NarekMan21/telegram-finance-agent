#!/usr/bin/env python3
"""
Test for group-based transaction type determination
"""

import json
import sys
import os

# Add the project directory to the path so we can import telegram_parser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_parser import TelegramFinancialParser

def test_group_based_parsing():
    """Test that transaction types are determined by group ID"""
    
    # Create a mock config with group types
    config = {
        "group_types": {
            "-1001234567890": "income",
            "-1000987654321": "expense"
        }
    }
    
    # Create parser instance with mock config
    parser = TelegramFinancialParser.__new__(TelegramFinancialParser)
    parser.config = config
    
    # Test cases
    test_cases = [
        # (message, group_id, expected_type)
        ("Получил зарплату 50000 руб", "-1001234567890", "income"),
        ("Купил продукты на 1500 руб", "-1000987654321", "expense"),
        ("Перевод от друга 10000 руб", "-1001234567890", "income"),
        ("Оплата интернета 700 руб", "-1000987654321", "expense"),
        ("Сообщение из неизвестной группы 1000 руб", "-1001111111111", None),  # Неизвестная группа
    ]
    
    print("Testing group-based transaction type determination...")
    
    for message, group_id, expected_type in test_cases:
        result = parser.parse_financial_message(message, group_id)
        
        if expected_type is None:
            # Для неизвестной группы ожидаем None
            if result is None:
                print(f"✓ Correctly ignored message from unknown group: {message}")
            else:
                print(f"✗ Expected None for unknown group, got: {result}")
        else:
            # Для известных групп проверяем тип
            if result and result['type'] == expected_type:
                print(f"✓ Correctly identified {expected_type}: {message}")
            else:
                print(f"✗ Failed to identify {expected_type}: {message}")
                if result:
                    print(f"  Got type: {result['type']}")
                else:
                    print(f"  No transaction detected")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_group_based_parsing()