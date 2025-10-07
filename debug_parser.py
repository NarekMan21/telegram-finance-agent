#!/usr/bin/env python3
"""
Debug script to check how many financial messages are found in each group
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from telegram_parser import TelegramFinancialParser

async def debug_parsing():
    """Debug parsing to see how many messages are found"""
    print("🔍 Debug Telegram Financial Parser")
    print("=" * 50)
    
    # Check if config exists
    config_path = Path('config.json')
    if not config_path.exists():
        print("❌ Config file config.json not found!")
        return
    
    # Load config to show group info
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    group_ids = config.get('group_ids', [])
    group_types = config.get('group_types', {})
    
    print(f"Configured groups:")
    for group_id in group_ids:
        group_type = group_types.get(str(group_id), "unknown")
        print(f"  {group_id} -> {group_type}")
    print()
    
    # Initialize parser
    parser = TelegramFinancialParser('config.json')
    
    # Initialize client
    print("Initializing Telegram client...")
    success = await parser.initialize_client()
    
    if not success:
        print("❌ Failed to initialize client")
        return
    
    print("✅ Client initialized successfully")
    print()
    
    # Check each group
    for group_id in group_ids:
        print(f"Checking group {group_id}...")
        
        # Fetch messages with different limits to see how many we can get
        limits_to_try = [100, 200, 500]
        
        for limit in limits_to_try:
            print(f"  Trying to fetch up to {limit} messages...")
            transactions = await parser.fetch_messages_from_group(str(group_id), limit=limit)
            print(f"    Found {len(transactions)} financial transactions")
            
            if len(transactions) > 0:
                print(f"    First transaction: {transactions[0]['description'][:50]}...")
                print(f"    Type: {transactions[0]['type']}")
                print(f"    Amount: {transactions[0]['amount']}")
            
            # If we found transactions, no need to try larger limits
            if len(transactions) > 0:
                break
        
        print()
    
    # Clean up
    if parser.client:
        await parser.client.disconnect()
    
    print("✅ Debug completed")

if __name__ == '__main__':
    try:
        asyncio.run(debug_parsing())
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()