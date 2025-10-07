#!/usr/bin/env python3
"""
Telegram Financial Agent - Web Server
Simple HTTP server for serving the web application
"""

import http.server
import socketserver
import json
import os
from pathlib import Path

class FinancialAgentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/transactions':
            self.handle_api_transactions()
        elif self.path == '/api/transactions/income':
            self.handle_api_transactions_income()
        elif self.path == '/api/transactions/expense':
            self.handle_api_transactions_expense()
        elif self.path == '/api/settings':
            self.handle_api_settings()
        else:
            # Serve static files
            if self.path == '/':
                self.path = '/index.html'
            
            # Check if file exists
            file_path = Path(__file__).parent / self.path.lstrip('/')
            if file_path.exists():
                super().do_GET()
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')
    
    def do_POST(self):
        if self.path == '/api/settings':
            self.handle_save_settings()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_api_transactions(self):
        try:
            # Load mock data
            transactions = [
                {
                    "id": "1",
                    "amount": 50000,
                    "type": "income",
                    "description": "Зарплата",
                    "category": "Работа",
                    "date": "2024-01-15T10:00:00Z",
                    "groupName": "Приходы"
                },
                {
                    "id": "2",
                    "amount": 1500,
                    "type": "expense",
                    "description": "Продукты",
                    "category": "Еда",
                    "date": "2024-01-14T15:30:00Z",
                    "groupName": "Расходы"
                },
                {
                    "id": "3",
                    "amount": 3000,
                    "type": "expense",
                    "description": "Коммунальные услуги",
                    "category": "ЖКХ",
                    "date": "2024-01-13T12:00:00Z",
                    "groupName": "Расходы"
                }
            ]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(transactions).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def handle_api_transactions_income(self):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([
                {
                    "id": "1",
                    "amount": 50000,
                    "type": "income",
                    "description": "Зарплата",
                    "category": "Работа",
                    "date": "2024-01-15T10:00:00Z",
                    "groupName": "Приходы"
                }
            ]).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def handle_api_transactions_expense(self):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([
                {
                    "id": "2",
                    "amount": 1500,
                    "type": "expense",
                    "description": "Продукты",
                    "category": "Еда",
                    "date": "2024-01-14T15:30:00Z",
                    "groupName": "Расходы"
                },
                {
                    "id": "3",
                    "amount": 3000,
                    "type": "expense",
                    "description": "Коммунальные услуги",
                    "category": "ЖКХ",
                    "date": "2024-01-13T12:00:00Z",
                    "groupName": "Расходы"
                }
            ]).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def handle_api_settings(self):
        try:
            config_path = Path(__file__).parent / 'config.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Remove sensitive data
            safe_config = {
                'currency': config.get('currency', 'RUB'),
                'notifications': config.get('notifications', True),
                'auto_update': config.get('auto_update', True),
                'update_interval': config.get('update_interval', 30)
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(safe_config).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def handle_save_settings(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            settings = json.loads(post_data.decode())
            
            # Save settings to config.json
            config_path = Path(__file__).parent / 'config.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config.update(settings)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

def run_server(host='0.0.0.0', port=8080):
    """Run the web server"""
    with socketserver.TCPServer((host, port), FinancialAgentHandler) as httpd:
        print(f"Server running at http://{host}:{port}")
        print(f"Open http://localhost:{port} in your browser")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == '__main__':
    import sys
    
    host = '0.0.0.0'
    port = 8080
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    run_server(host, port)