#!/usr/bin/env python3
"""
Fixed Telegram Financial Agent - Flask Web Application
Works without Telethon dependencies
"""

import json
import logging
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, render_template, request

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')  # Указываем правильную папку для шаблонов

class FinancialAgentApp:
    def __init__(self):
        self.transactions = []
        self.is_parsing = False
        self.last_update = None
        self.load_existing_data()
    
    def load_existing_data(self):
        """Load existing transactions from file"""
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
                        transaction = {
                            'id': str(t.get('id', '')),
                            'amount': t.get('amount', 0),
                            'type': 'income',
                            'description': t.get('description', t.get('text', '')),
                            'category': 'другое',  # Default category
                            'date': t.get('timestamp', t.get('date', datetime.now().isoformat())),
                            'group_id': t.get('group_id', ''),
                            'group_name': t.get('group_title', t.get('group_name', 'Unknown'))
                        }
                        unified_transactions.append(transaction)
                        logger.debug(f"Income transaction date: {transaction['date']}")
                    
                    # Process expense transactions
                    for t in expense_transactions:
                        transaction = {
                            'id': str(t.get('id', '')),
                            'amount': t.get('amount', 0),
                            'type': 'expense',
                            'description': t.get('description', t.get('text', '')),
                            'category': 'другое',  # Default category
                            'date': t.get('timestamp', t.get('date', datetime.now().isoformat())),
                            'group_id': t.get('group_id', ''),
                            'group_name': t.get('group_title', t.get('group_name', 'Unknown'))
                        }
                        unified_transactions.append(transaction)
                        logger.debug(f"Expense transaction date: {transaction['date']}")
                    
                    self.transactions = unified_transactions
                    logger.info(f"Loaded {len(income_transactions)} income and {len(expense_transactions)} expense transactions")
                else:
                    # Old format - list of transactions
                    # Convert to unified format
                    unified_transactions = []
                    for t in data:
                        # Determine transaction type based on group_id or other criteria
                        # For now, we'll use a simple heuristic
                        if 'type' in t:
                            transaction_type = t['type']
                        else:
                            # Try to determine type from group_id or amount context
                            if str(t.get('group_id', '')).endswith('9306') or 'ПРИХОД' in str(t.get('group_name', '')):
                                transaction_type = 'income'
                            else:
                                transaction_type = 'expense'
                        
                        transaction = {
                            'id': str(t.get('id', '')),
                            'amount': t.get('amount', 0),
                            'type': transaction_type,
                            'description': t.get('description', t.get('text', '')),
                            'category': t.get('category', 'другое'),
                            'date': t.get('timestamp', t.get('date', datetime.now().isoformat())),
                            'group_id': t.get('group_id', ''),
                            'group_name': t.get('group_title', t.get('group_name', 'Unknown'))
                        }
                        unified_transactions.append(transaction)
                        logger.debug(f"Old format transaction date: {transaction['date']}")
                    
                    self.transactions = unified_transactions
                    logger.info(f"Loaded {len(data)} existing transactions from old format")
            else:
                logger.info("No existing transactions file found")
                self.transactions = []
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
            self.transactions = []
    
    def simulate_telegram_parsing(self):
        """Simulate parsing data from Telegram (for testing purposes)"""
        # Generate some random transactions to simulate new data from Telegram
        new_transactions = []
        
        # Add some random income transactions
        for i in range(random.randint(1, 3)):
            new_transactions.append({
                'id': str(int(datetime.now().timestamp() * 1000000) + i),
                'amount': random.randint(1000, 50000),
                'type': 'income',
                'description': f'Доход #{len(self.transactions) + i + 1}',
                'category': 'другое',
                'date': datetime.now().isoformat(),
                'group_id': '-4855539306',
                'group_name': 'ПРИХОД'
            })
        
        # Add some random expense transactions
        for i in range(random.randint(1, 3)):
            new_transactions.append({
                'id': str(int(datetime.now().timestamp() * 1000000) + 1000 + i),
                'amount': random.randint(100, 10000),
                'type': 'expense',
                'description': f'Расход #{len(self.transactions) + i + 1}',
                'category': 'другое',
                'date': datetime.now().isoformat(),
                'group_id': '-4884869527',
                'group_name': 'РАССХОД'
            })
        
        # Add new transactions to existing ones
        self.transactions.extend(new_transactions)
        
        # Update last update time
        self.last_update = datetime.now()
        
        # Save to file
        self.save_transactions_to_file()
        
        logger.info(f"Simulated parsing completed. Added {len(new_transactions)} new transactions.")
        return True
    
    def save_transactions_to_file(self):
        """Save transactions to file in the original format"""
        try:
            # Separate transactions by type
            income_transactions = [t for t in self.transactions if t['type'] == 'income']
            expense_transactions = [t for t in self.transactions if t['type'] == 'expense']
            
            # Convert back to original format
            data = {
                "income": income_transactions,
                "expense": expense_transactions
            }
            
            # Save to file
            with open('transactions.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved {len(income_transactions)} income and {len(expense_transactions)} expense transactions to file")
        except Exception as e:
            logger.error(f"Error saving transactions to file: {e}")
    
    def clear_all_data(self):
        """Clear all transaction data"""
        self.transactions = []
        self.last_update = datetime.now()
        self.save_transactions_to_file()
        logger.info("All data cleared")
    
    def get_transactions_summary(self) -> Dict:
        """Get transactions summary statistics"""
        total_income = sum(t['amount'] for t in self.transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in self.transactions if t['type'] == 'expense')
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'income_count': len([t for t in self.transactions if t['type'] == 'income']),
            'expense_count': len([t for t in self.transactions if t['type'] == 'expense']),
            'total_count': len(self.transactions),
            'last_update': self.last_update.isoformat() if self.last_update else None
        }

# Initialize the app
financial_app = FinancialAgentApp()

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

# Additional routes for .html extensions (for compatibility with client-side navigation)
@app.route('/index.html')
def index_html():
    """Serve the main application"""
    return render_template('index.html')

@app.route('/transactions.html')
def transactions_page():
    """Serve transactions page"""
    return render_template('transactions.html')

@app.route('/analytics.html')
def analytics_page():
    """Serve analytics page"""
    return render_template('analytics.html')

@app.route('/settings.html')
def settings_page():
    """Serve settings page"""
    return render_template('settings.html')

@app.route('/settings_test.html')
def settings_test_page():
    """Serve settings test page"""
    return render_template('settings_test.html')

# Additional routes without .html extension (new format)
@app.route('/transactions')
def transactions_page_no_ext():
    """Serve transactions page"""
    return render_template('transactions.html')

@app.route('/analytics')
def analytics_page_no_ext():
    """Serve analytics page"""
    return render_template('analytics.html')

@app.route('/settings')
def settings_page_no_ext():
    """Serve settings page"""
    return render_template('settings_test.html')

@app.route('/api/transactions')
def api_transactions():
    """Get all transactions"""
    try:
        # Get query parameters
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int, default=0)
        transaction_type = request.args.get('type')
        
        # Filter transactions
        filtered_transactions = financial_app.transactions
        
        if transaction_type:
            filtered_transactions = [t for t in filtered_transactions if t['type'] == transaction_type]
        
        # Apply pagination
        if limit:
            filtered_transactions = filtered_transactions[offset:offset + limit]
        else:
            filtered_transactions = filtered_transactions[offset:]
        
        return jsonify({
            'success': True,
            'data': filtered_transactions,
            'total': len(financial_app.transactions),
            'filtered': len(filtered_transactions)
        })
    
    except Exception as e:
        logger.error(f"Error in api_transactions: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        })

@app.route('/api/transactions/income')
def api_transactions_income():
    """Get income transactions only"""
    income_transactions = [t for t in financial_app.transactions if t['type'] == 'income']
    return jsonify({
        'success': True,
        'data': income_transactions,
        'count': len(income_transactions)
    })

@app.route('/api/transactions/expense')
def api_transactions_expense():
    """Get expense transactions only"""
    expense_transactions = [t for t in financial_app.transactions if t['type'] == 'expense']
    return jsonify({
        'success': True,
        'data': expense_transactions,
        'count': len(expense_transactions)
    })

@app.route('/api/summary')
def api_summary():
    """Get transactions summary"""
    try:
        summary = financial_app.get_transactions_summary()
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

@app.route('/api/status')
def api_status():
    """Get application status"""
    return jsonify({
        'success': True,
        'data': {
            'is_parsing': financial_app.is_parsing,
            'last_update': financial_app.last_update.isoformat() if financial_app.last_update else None,
            'transaction_count': len(financial_app.transactions),
            'server_time': datetime.now().isoformat()
        }
    })

@app.route('/api/update', methods=['POST'])
def api_force_update():
    """Force data update (simulate Telegram parsing)"""
    try:
        financial_app.is_parsing = True
        success = financial_app.simulate_telegram_parsing()
        financial_app.is_parsing = False
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Data updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update data'
            })
    except Exception as e:
        financial_app.is_parsing = False
        logger.error(f"Error in api_force_update: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/clear-data', methods=['POST'])
def api_clear_data():
    """Clear all transaction data"""
    try:
        financial_app.clear_all_data()
        return jsonify({
            'success': True,
            'message': 'All data cleared successfully'
        })
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Static file serving
@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    if filename.endswith('.js'):
        return app.send_static_file(filename)
    elif filename.endswith('.css'):
        return app.send_static_file(filename)
    else:
        return app.send_static_file(filename)

def run_app(host='0.0.0.0', port=8080, debug=False):
    """Run the Flask application"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    import sys
    
    host = '0.0.0.0'
    port = 8080
    debug = False
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    if len(sys.argv) > 3:
        debug = sys.argv[3].lower() == 'true'
    
    print(f"Starting Telegram Financial Agent on http://{host}:{port}")
    run_app(host, port, debug)