#!/usr/bin/env python3
"""
Simple startup script for Telegram Financial Agent
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("🚀 Starting Telegram Financial Agent...")
    print("=====================================")
    
    # Get configuration from config.json
    try:
        import json
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        web_config = config.get('web_server', {})
        host = web_config.get('host', '0.0.0.0')
        port = web_config.get('port', 8080)
        debug = web_config.get('debug', False)
        
        print(f"📡 Server: http://{host}:{port}")
        print(f"🔧 Debug mode: {debug}")
        print("💡 Press Ctrl+C to stop the server")
        print()
        
        # Run the Flask app
        app.run(host=host, port=port, debug=debug)
        
    except FileNotFoundError:
        print("❌ Error: config.json file not found!")
        print("Please create a config.json file with your settings.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting the application: {e}")
        sys.exit(1)