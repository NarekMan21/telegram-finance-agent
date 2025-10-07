#!/usr/bin/env python3
"""
Test script for Telegram parser
"""

import asyncio
import json
from telegram_parser import TelegramFinancialParser

async def test_parser():
    """Test the Telegram parser"""
    print("Testing Telegram parser...")
    
    try:
        # Initialize parser
        parser = TelegramFinancialParser('config.json')
        print("Parser initialized")
        
        # Initialize client
        success = await parser.initialize_client()
        if not success:
            print("Failed to initialize client")
            return
        
        print("Client initialized successfully")
        
        # Get group IDs from config
        group_ids = parser.config.get('group_ids', [])
        print(f"Found {len(group_ids)} groups in config")
        
        # Fetch messages from each group
        all_transactions = []
        for group_info in group_ids:
            group_id = group_info['id']
            group_name = group_info['name']
            print(f"\nFetching messages from group: {group_name} ({group_id})")
            
            try:
                transactions = await parser.fetch_messages_from_group(group_id, limit=10)
                print(f"Found {len(transactions)} transactions in {group_name}")
                all_transactions.extend(transactions)
            except Exception as e:
                print(f"Error fetching messages from {group_name}: {e}")
        
        # Save transactions to file
        if all_transactions:
            # Load existing data
            try:
                with open('transactions.json', 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                existing_data = {"income": [], "expense": []}
            
            # Separate transactions by type
            income_transactions = [t for t in all_transactions if t['type'] == 'income']
            expense_transactions = [t for t in all_transactions if t['type'] == 'expense']
            
            # Update existing data
            existing_data["income"].extend(income_transactions)
            existing_data["expense"].extend(expense_transactions)
            
            # Save updated data
            with open('transactions.json', 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            print(f"\nSaved {len(income_transactions)} income and {len(expense_transactions)} expense transactions")
        else:
            print("No transactions found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_parser())