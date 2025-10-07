#!/usr/bin/env python3
"""
Simple server for testing data display
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def load_transactions():
    """Load transactions from file"""
    try:
        transactions_file = Path('transactions.json')
        if transactions_file.exists():
            with open(transactions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both old and new formats
            if isinstance(data, dict):
                # New format with separate income and expense arrays
                income_transactions = data.get('income', [])
                expense_transactions = data.get('expense', [])
                
                # Convert to unified format
                unified_transactions = []
                
                # Process income transactions
                for t in income_transactions:
                    unified_transactions.append({
                        'id': str(t.get('id', '')),
                        'amount': t.get('amount', 0),
                        'type': 'income',
                        'description': t.get('description', t.get('text', '')),
                        'category': 'другое',  # Default category
                        'date': t.get('date', datetime.now().isoformat()),
                        'group_id': t.get('group_id', ''),
                        'group_name': t.get('group_name', 'Unknown')
                    })
                
                # Process expense transactions
                for t in expense_transactions:
                    unified_transactions.append({
                        'id': str(t.get('id', '')),
                        'amount': t.get('amount', 0),
                        'type': 'expense',
                        'description': t.get('description', t.get('text', '')),
                        'category': 'другое',  # Default category
                        'date': t.get('date', datetime.now().isoformat()),
                        'group_id': t.get('group_id', ''),
                        'group_name': t.get('group_name', 'Unknown')
                    })
                
                logger.info(f"Loaded {len(income_transactions)} income and {len(expense_transactions)} expense transactions")
                return unified_transactions
            else:
                # Old format - list of transactions
                logger.info(f"Loaded {len(data)} existing transactions")
                return data
        else:
            logger.info("No existing transactions file found")
            return []
    except Exception as e:
        logger.error(f"Error loading existing data: {e}")
        return []

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

@app.route('/test')
def test():
    """Serve the test page"""
    return render_template('test_display.html')

@app.route('/api/transactions')
def api_transactions():
    """Get all transactions"""
    try:
        transactions = load_transactions()
        
        return jsonify({
            'success': True,
            'data': transactions,
            'total': len(transactions),
            'filtered': len(transactions)
        })
    
    except Exception as e:
        logger.error(f"Error in api_transactions: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        })

@app.route('/api/summary')
def api_summary():
    """Get transactions summary"""
    try:
        transactions = load_transactions()
        
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        
        summary = {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'income_count': len([t for t in transactions if t['type'] == 'income']),
            'expense_count': len([t for t in transactions if t['type'] == 'expense']),
            'total_count': len(transactions),
            'last_update': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        logger.error(f"Error in api_summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    if filename.endswith('.js'):
        return app.send_static_file(filename)
    elif filename.endswith('.css'):
        return app.send_static_file(filename)
    else:
        return app.send_static_file(filename)

if __name__ == '__main__':
    print("Starting simple server on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)