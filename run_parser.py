#!/usr/bin/env python3
"""
Telegram Financial Agent - Real-time Parser Runner
This script runs the Telegram parser in real-time monitoring mode
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from telegram_parser import TelegramFinancialParser

async def main():
    """Main function to run the real-time parser"""
    print("🚀 Telegram Financial Agent - Real-time Parser")
    print("=" * 50)
    
    # Check if config exists
    config_path = Path('config.json')
    if not config_path.exists():
        print("❌ Config file config.json not found!")
        print("Please create config.json with your Telegram API credentials")
        return
    
    # Initialize parser
    parser = TelegramFinancialParser('config.json')
    
    try:
        print("📡 Starting real-time monitoring...")
        print("Press Ctrl+C to stop")
        print("-" * 30)
        
        # Start real-time monitoring
        success = await parser.start_real_time_monitoring()
        
        if not success:
            print("❌ Failed to start monitoring")
            return
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping parser...")
        parser.stop()
        print("✅ Parser stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        parser.stop()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")