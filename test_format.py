#!/usr/bin/env python3
"""
Test script to check the new transaction format
"""

import json
import os
from datetime import datetime

def test_format():
    """Test the new transaction format"""
    print("Testing transaction format...")
    
    # Create sample data in ParserQ format
    sample_data = {
        "income": [
            {
                "id": 1,
                "timestamp": datetime.now().isoformat(),
                "group_id": -4855539306,
                "group_title": "ПРИХОД",
                "text": "Тестовый доход 10000",
                "sender_id": 123456789,
                "amount": 10000.0,
                "currency": "RUB",
                "description": "Тестовый доход 10000"
            }
        ],
        "expense": [
            {
                "id": 2,
                "timestamp": datetime.now().isoformat(),
                "group_id": -4884869527,
                "group_title": "РАССХОД",
                "text": "Тестовый расход 5000",
                "sender_id": 123456789,
                "amount": 5000.0,
                "currency": "RUB",
                "description": "Тестовый расход 5000"
            }
        ],
        "last_updated": datetime.now().isoformat()
    }
    
    # Save to file
    with open('test_transactions.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print("Sample data saved to test_transactions.json")
    print("Format matches ParserQ format:")
    print(json.dumps(sample_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_format()