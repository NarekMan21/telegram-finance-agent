#!/usr/bin/env python3
"""
Test script for data loading
"""

import json
from app import FinancialAgentApp

def test_data_loading():
    """Test data loading functionality"""
    print("Testing data loading...")
    
    # Create app instance
    app = FinancialAgentApp()
    
    print(f"Loaded {len(app.transactions)} transactions")
    
    # Print first few transactions
    for i, transaction in enumerate(app.transactions[:5]):
        print(f"{i+1}. {transaction['type']} {transaction['amount']}₽ - {transaction['description'][:50]}...")
    
    # Test API endpoint
    print("\nTesting API endpoint...")
    try:
        # Simulate API call
        filtered_transactions = app.transactions
        
        print(f"API would return {len(filtered_transactions)} transactions")
        
        # Print sample data in API format
        sample_data = filtered_transactions[:3] if len(filtered_transactions) > 0 else []
        print("Sample data:")
        for transaction in sample_data:
            print(f"  - {transaction['type']} {transaction['amount']}₽ - {transaction['description'][:30]}...")
            
    except Exception as e:
        print(f"Error testing API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_loading()