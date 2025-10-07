#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to clean up duplicate transactions in transactions.json file
"""

import json
import os
from datetime import datetime

def clean_duplicates():
    """Remove duplicate transactions from transactions.json"""
    transactions_file = 'transactions.json'
    
    if not os.path.exists(transactions_file):
        print("transactions.json file not found")
        return
    
    try:
        # Load existing transactions
        with open(transactions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if data is in the correct format
        if 'income' not in data or 'expense' not in data:
            print("Invalid data format in transactions.json")
            return
        
        # Remove duplicates from income transactions
        seen_income_ids = set()
        unique_income = []
        for transaction in data['income']:
            transaction_id = str(transaction.get('id'))
            if transaction_id not in seen_income_ids:
                seen_income_ids.add(transaction_id)
                unique_income.append(transaction)
        
        # Remove duplicates from expense transactions
        seen_expense_ids = set()
        unique_expense = []
        for transaction in data['expense']:
            transaction_id = str(transaction.get('id'))
            if transaction_id not in seen_expense_ids:
                seen_expense_ids.add(transaction_id)
                unique_expense.append(transaction)
        
        # Update the data with unique transactions
        data['income'] = unique_income
        data['expense'] = unique_expense
        data['last_updated'] = datetime.now().isoformat()
        
        # Save cleaned data back to file
        with open(transactions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Cleaned up duplicates: {len(data['income'])} income and {len(data['expense'])} expense transactions")
        
    except Exception as e:
        print(f"Error cleaning duplicates: {e}")

if __name__ == '__main__':
    clean_duplicates()