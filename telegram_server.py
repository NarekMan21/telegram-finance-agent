#!/usr/bin/env python3
"""
Simple server for testing Telegram Mini App
"""

import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Serve the main Telegram Mini App
@app.route('/')
def telegram_mini_app():
    return send_from_directory('templates', 'telegram_index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)