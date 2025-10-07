#!/usr/bin/env python3
"""
Simple script to check if a port is open
"""

import socket
import sys

def check_port(host, port):
    """Check if a port is open on a host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is open on {host}")
            return True
        else:
            print(f"❌ Port {port} is closed on {host}")
            return False
    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False

if __name__ == '__main__':
    host = 'localhost'
    port = 8080
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    print(f"🔍 Checking if {host}:{port} is open...")
    check_port(host, port)