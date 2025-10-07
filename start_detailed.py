#!/usr/bin/env python3
"""
Detailed startup script for Telegram Financial Agent
"""

import os
import sys
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import socketserver

class DetailedHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Print detailed log messages
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")
        super().log_message(format, *args)

def start_server(host='localhost', port=8080):
    """Start the HTTP server with detailed logging"""
    print(f"🚀 Starting Telegram Financial Agent Web Server...")
    print(f"📍 Host: {host}")
    print(f"📍 Port: {port}")
    print(f"📂 Serving files from: {os.getcwd()}")
    print("-" * 50)
    
    try:
        # Change to the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"📁 Changed to directory: {script_dir}")
        
        # Start the server
        with socketserver.TCPServer((host, port), DetailedHandler) as httpd:
            print(f"✅ Server started successfully!")
            print(f"🌐 Access the application at: http://{host}:{port}")
            print(f"💡 Press Ctrl+C to stop the server")
            print("=" * 50)
            
            # Serve requests
            httpd.serve_forever()
            
    except PermissionError:
        print("❌ Permission denied. Try running with different port:")
        print("   python start_detailed.py 8081")
        return 1
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Port is already in use. Try a different port:")
            print("   python start_detailed.py 8081")
        else:
            print(f"❌ OS Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    # Get port from command line arguments or use default
    port = 8080
    host = 'localhost'
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 8080")
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    sys.exit(start_server(host, port))