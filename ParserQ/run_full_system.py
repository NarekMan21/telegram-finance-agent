import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Data file path
DATA_FILE = 'transactions.json'

# Default empty data
default_data = {
    'income': [],
    'expense': [],
    'last_updated': datetime.now().isoformat()
}

def load_data():
    """Load data from file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return default_data
    else:
        # Create empty data file if it doesn't exist
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            return default_data
        except Exception as e:
            logger.error(f"Error creating data file: {e}")
            return default_data

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/':
            # Serve the main page
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            with open('templates/index.html', 'rb') as f:
                self.wfile.write(f.read())
                
        elif parsed_path.path == '/api/transactions/income':
            # Serve income transactions
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            data = load_data()
            self.wfile.write(json.dumps(data['income'], ensure_ascii=False).encode('utf-8'))
            
        elif parsed_path.path == '/api/transactions/expense':
            # Serve expense transactions
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            data = load_data()
            self.wfile.write(json.dumps(data['expense'], ensure_ascii=False).encode('utf-8'))
            
        elif parsed_path.path == '/api/transactions':
            # Serve all transactions
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            data = load_data()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            
        else:
            # Serve static files
            if parsed_path.path.startswith('/static/'):
                # Remove /static/ prefix
                file_path = parsed_path.path[1:]
            else:
                file_path = parsed_path.path[1:] if parsed_path.path != '/' else 'templates/index.html'
                
            try:
                with open(file_path, 'rb') as f:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')

def run_server():
    """Run the HTTP server"""
    server = HTTPServer(('localhost', 5000), RequestHandler)
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")

def update_data_periodically():
    """Update data from Telegram periodically"""
    import subprocess
    import os
    
    while True:
        try:
            logger.info("Updating data from Telegram...")
            
            # Run the fetch script
            result = subprocess.run(['python', 'fetch_telegram_data.py'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                logger.info("Data updated successfully")
            else:
                logger.error(f"Error updating data: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error updating data: {e}")
        
        # Wait 30 seconds before next update
        time.sleep(30)

if __name__ == '__main__':
    # Start the data update thread
    update_thread = threading.Thread(target=update_data_periodically, daemon=True)
    update_thread.start()
    
    # Run the server
    run_server()