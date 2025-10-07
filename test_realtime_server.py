#!/usr/bin/env python3
"""
Simple test server for real-time data updates
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global data
transactions_data = {
    "income": [],
    "expense": []
}

def load_data():
    """Load data from file"""
    global transactions_data
    transactions_file = Path('transactions.json')
    
    if transactions_file.exists():
        try:
            with open(transactions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            transactions_data = data
        except Exception as e:
            print(f"Error loading data: {e}")

def save_data():
    """Save data to file"""
    transactions_file = Path('transactions.json')
    try:
        with open(transactions_file, 'w', encoding='utf-8') as f:
            json.dump(transactions_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving data: {e}")

def simulate_data_updates():
    """Simulate real-time data updates"""
    global transactions_data
    
    # Create initial data
    transactions_data = {
        "income": [
            {"id": "1", "amount": 1000, "description": "Зарплата", "timestamp": datetime.now().isoformat()},
        ],
        "expense": [
            {"id": "2", "amount": 500, "description": "Продукты", "timestamp": datetime.now().isoformat()},
        ]
    }
    
    save_data()
    print("Initial data written")
    
    # Simulate periodic updates
    for i in range(10):
        time.sleep(3)  # Update every 3 seconds
        
        # Add new transaction
        new_income = {
            "id": str(i + 3),
            "amount": 100 * (i + 1),
            "description": f"Доход {i + 1}",
            "timestamp": datetime.now().isoformat()
        }
        
        transactions_data["income"].append(new_income)
        save_data()
        print(f"Updated data written: {len(transactions_data['income'])} income, {len(transactions_data['expense'])} expense transactions")

@app.route('/api/transactions')
def api_transactions():
    """Get all transactions"""
    load_data()  # Load fresh data from file
    
    # Convert to unified format
    unified_transactions = []
    
    # Process income transactions
    for t in transactions_data.get('income', []):
        unified_transactions.append({
            'id': str(t.get('id', '')),
            'amount': t.get('amount', 0),
            'type': 'income',
            'description': t.get('description', ''),
            'category': 'другое',
            'date': t.get('timestamp', datetime.now().isoformat()),
        })
    
    # Process expense transactions
    for t in transactions_data.get('expense', []):
        unified_transactions.append({
            'id': str(t.get('id', '')),
            'amount': t.get('amount', 0),
            'type': 'expense',
            'description': t.get('description', ''),
            'category': 'другое',
            'date': t.get('timestamp', datetime.now().isoformat()),
        })
    
    return jsonify({
        'success': True,
        'data': unified_transactions,
        'total': len(unified_transactions),
        'filtered': len(unified_transactions)
    })

@app.route('/api/transactions/last-update')
def api_transactions_last_update():
    """Get timestamp of last data update"""
    load_data()  # Load fresh data from file
    
    # Find the latest timestamp
    latest_timestamp = None
    all_transactions = transactions_data.get('income', []) + transactions_data.get('expense', [])
    
    for t in all_transactions:
        timestamp = t.get('timestamp')
        if timestamp and (latest_timestamp is None or timestamp > latest_timestamp):
            latest_timestamp = timestamp
    
    return jsonify({
        'success': True,
        'data': {
            'last_update': latest_timestamp,
            'transaction_count': len(all_transactions),
            'is_parsing': False
        }
    })

if __name__ == '__main__':
    # Start data update simulation in a separate thread
    update_thread = threading.Thread(target=simulate_data_updates, daemon=True)
    update_thread.start()
    
    # Run Flask server
    app.run(host='0.0.0.0', port=8080, debug=True)