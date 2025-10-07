#!/usr/bin/env python3
"""
Debug script to check what messages are in groups and why they're not recognized as financial
"""

import asyncio
import json
import sys
import os
import re
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from telegram_parser import TelegramFinancialParser

async def debug_messages():
    """Debug messages to see what's in the groups"""
    print("🔍 Debug Telegram Messages")
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
        group_type = group_types.get(str(group_id), "unknown")
        print(f"Checking group {group_id} ({group_type})...")
        
        if not parser.client:
            print("  ❌ Client not available")
            continue
            
        try:
            # Get entity (group)
            entity = await parser.client.get_entity(int(group_id))
            group_name = getattr(entity, 'title', 'Unknown Group')
            print(f"  Group name: {group_name}")
            
            # Fetch recent messages (just 10 for debugging)
            print(f"  Fetching 10 recent messages...")
            messages = []
            async for message in parser.client.iter_messages(entity, limit=10):
                if message.text:
                    messages.append(message)
            
            print(f"  Found {len(messages)} messages with text")
            
            # Show details of each message
            for i, message in enumerate(messages):
                print(f"    Message {i+1}:")
                print(f"      ID: {message.id}")
                print(f"      Date: {message.date}")
                print(f"      Text: {message.text[:100]}{'...' if len(message.text) > 100 else ''}")
                
                # Try to parse as financial message
                parsed_data = parser.parse_financial_message(message.text, str(group_id))
                if parsed_data:
                    print(f"      ✅ Recognized as financial:")
                    print(f"         Amount: {parsed_data['amount']}")
                    print(f"         Type: {parsed_data['type']}")
                    print(f"         Category: {parsed_data['category']}")
                else:
                    print(f"      ❌ Not recognized as financial")
                    
                    # Try to find amount pattern
                    amount_pattern = r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:₽|руб|RUB)'
                    amount_match = re.search(amount_pattern, message.text)
                    if amount_match:
                        print(f"         Amount pattern found: {amount_match.group()}")
                    else:
                        print(f"         No amount pattern found")
                
                print()
            
        except Exception as e:
            print(f"  ❌ Error checking group: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Clean up
    if parser.client:
        await parser.client.disconnect()
    
    print("✅ Debug completed")

if __name__ == '__main__':
    try:
        asyncio.run(debug_messages())
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()