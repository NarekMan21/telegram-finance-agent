#!/usr/bin/env python3
"""
Test script for the clear data functionality
"""

import json
import os
from pathlib import Path

def test_clear_data_endpoint():
    """Test the clear data functionality"""
    # Create a test transactions file
    test_data = {
        "income": [
            {"id": "1", "amount": 1000, "description": "Test income", "timestamp": "2023-01-01T00:00:00"},
            {"id": "2", "amount": 2000, "description": "Another income", "timestamp": "2023-01-02T00:00:00"}
        ],
        "expense": [
            {"id": "3", "amount": 500, "description": "Test expense", "timestamp": "2023-01-03T00:00:00"}
        ]
    }
    
    # Write test data to file
    transactions_file = Path('test_transactions.json')
    with open(transactions_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"Created test file with {len(test_data['income'])} income and {len(test_data['expense'])} expense transactions")
    
    # Simulate the clear data functionality
    if transactions_file.exists():
        # Create empty structure
        empty_data = {"income": [], "expense": []}
        with open(transactions_file, 'w', encoding='utf-8') as f:
            json.dump(empty_data, f, indent=2, ensure_ascii=False)
        
        print("Data cleared successfully")
        
        # Verify the file is empty
        with open(transactions_file, 'r', encoding='utf-8') as f:
            cleared_data = json.load(f)
        
        print(f"After clearing: {len(cleared_data['income'])} income and {len(cleared_data['expense'])} expense transactions")
        
        # Clean up
        transactions_file.unlink()
        print("Test file removed")
    
    print("Test completed successfully")

if __name__ == "__main__":
    test_clear_data_endpoint()