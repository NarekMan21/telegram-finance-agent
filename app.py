#!/usr/bin/env python3
"""
Telegram Financial Agent - Flask Web Application
Integrated with real Telegram data parsing
"""

import asyncio
import json
import logging
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, render_template, request

# Import our Telegram parser
from telegram_parser import TelegramFinancialParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Try to import flask_cors, but continue if it's not available
try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    print("Warning: flask_cors not available, CORS support disabled")

class FinancialAgentApp:
    def __init__(self):
        self.parser = TelegramFinancialParser('config.json')
        self.transactions = []
        self.is_parsing = False
        self.last_update = None
        self.load_existing_data()
        
        # Start background parsing thread
        self.start_background_parsing()
    
    def load_existing_data(self):
        """Load existing transactions from file in ParserQ format"""
        try:
            # Загружаем данные из файла transactions.json в директории ParserQ
            transactions_file = Path('ParserQ/transactions.json')
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
                            'date': t.get('timestamp', t.get('date', datetime.now().isoformat())),
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
                            'date': t.get('timestamp', t.get('date', datetime.now().isoformat())),
                            'group_id': t.get('group_id', ''),
                            'group_name': t.get('group_name', 'Unknown')
                        })
                    
                    self.transactions = unified_transactions
                    logger.info(f"Loaded {len(income_transactions)} income and {len(expense_transactions)} expense transactions")
                else:
                    # Old format - list of transactions
                    self.transactions = data
                    logger.info(f"Loaded {len(data)} existing transactions")
            else:
                logger.info("No existing transactions file found")
                self.transactions = []
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
            self.transactions = []
    
    def start_background_parsing(self):
        """Start background parsing in a separate thread"""
        def parse_worker():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                self.is_parsing = True
                logger.info("Starting background Telegram parsing...")
                
                success = loop.run_until_complete(self.parser.start_parsing())
                
                if success:
                    # Reload transactions after parsing
                    self.load_existing_data()
                    self.last_update = datetime.now()
                    logger.info("Background parsing completed successfully")
                else:
                    logger.error("Background parsing failed")
                
                self.is_parsing = False
                
            except Exception as e:
                logger.error(f"Error in background parsing: {e}")
                self.is_parsing = False
        
        # Start parsing thread only if not already parsing
        if not self.is_parsing:
            thread = threading.Thread(target=parse_worker, daemon=True)
            thread.start()
    
    def force_update(self):
        """Force immediate data update"""
        # Always start parsing, even if already parsing (will be queued)
        self.start_background_parsing()
        return True
    
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
    try:
        return render_template('transactions.html')
    except Exception as e:
        logger.error(f"Error serving transactions.html: {e}")
        return f"Error loading transactions page: {str(e)}", 500

@app.route('/analytics.html')
def analytics_page():
    """Serve analytics page"""
    try:
        return render_template('analytics.html')
    except Exception as e:
        logger.error(f"Error serving analytics.html: {e}")
        return f"Error loading analytics page: {str(e)}", 500

@app.route('/settings.html')
def settings_page():
    """Serve settings page"""
    try:
        # Log template directory
        template_dir = app.template_folder or 'templates'
        logger.info(f"Template directory: {template_dir}")
        
        # Check if template file exists
        import os
        template_path = os.path.join(template_dir, 'settings.html')
        if os.path.exists(template_path):
            logger.info(f"Template file exists: {template_path}")
        else:
            logger.error(f"Template file does not exist: {template_path}")
            return "Template file not found", 404
            
        return render_template('settings.html')
    except Exception as e:
        logger.error(f"Error serving settings.html: {e}")
        # Fallback to a simple response
        return f"Error loading settings page: {str(e)}", 500

# Additional routes without .html extension (new format)
@app.route('/transactions')
def transactions_page_no_ext():
    """Serve transactions page"""
    try:
        return render_template('transactions.html')
    except Exception as e:
        logger.error(f"Error serving transactions page: {e}")
        return f"Error loading transactions page: {str(e)}", 500

@app.route('/analytics')
def analytics_page_no_ext():
    """Serve analytics page"""
    try:
        return render_template('analytics.html')
    except Exception as e:
        logger.error(f"Error serving analytics page: {e}")
        return f"Error loading analytics page: {str(e)}", 500

@app.route('/settings')
def settings_page_no_ext():
    """Serve settings page"""
    try:
        # Log template directory
        template_dir = app.template_folder or 'templates'
        logger.info(f"Template directory: {template_dir}")
        
        # Check if template file exists
        import os
        template_path = os.path.join(template_dir, 'settings.html')
        if os.path.exists(template_path):
            logger.info(f"Template file exists: {template_path}")
        else:
            logger.error(f"Template file does not exist: {template_path}")
            return "Template file not found", 404
            
        return render_template('settings.html')
    except Exception as e:
        logger.error(f"Error serving settings page: {e}")
        return f"Error loading settings page: {str(e)}", 500

@app.route('/telegram')
def telegram_app():
    """Serve the Telegram Mini App version"""
    return render_template('telegram_index.html')

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

@app.route('/api/transactions/last-update')
def api_transactions_last_update():
    """Get timestamp of last data update"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'last_update': financial_app.last_update.isoformat() if financial_app.last_update else None,
                'transaction_count': len(financial_app.transactions),
                'is_parsing': financial_app.is_parsing
            }
        })
    except Exception as e:
        logger.error(f"Error in api_transactions_last_update: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
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

@app.route('/api/settings', methods=['GET'])
def api_settings_get():
    """Get current settings"""
    try:
        config_path = Path('config.json')
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Return safe config (without sensitive data)
            safe_config = {
                'currency': config.get('currency', 'RUB'),
                'notifications': config.get('notifications', True),
                'auto_update': config.get('auto_update', True),
                'update_interval': config.get('update_interval', 30),
                'group_ids': config.get('group_ids', [])
            }
            
            return jsonify({
                'success': True,
                'data': safe_config
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Config file not found'
            })
    
    except Exception as e:
        logger.error(f"Error in api_settings_get: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/settings', methods=['POST'])
def api_settings_post():
    """Update settings"""
    try:
        new_settings = request.get_json()
        
        config_path = Path('config.json')
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update config with new settings
        config.update(new_settings)
        
        # Обновляем group_types на основе новых групп
        if 'group_ids' in new_settings:
            # Предполагаем, что первая группа - расходы, вторая - доходы (или наоборот)
            # В реальном приложении это должно быть настраиваемо
            group_types = {}
            for i, group in enumerate(new_settings['group_ids']):
                if isinstance(group, dict):
                    group_id = group['id']
                else:
                    group_id = group
                
                # Простое распределение: первая группа - расходы, вторая - доходы
                group_type = 'expense' if i == 0 else 'income' if i == 1 else 'other'
                group_types[group_id] = group_type
            
            config['group_types'] = group_types
        
        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        # Также обновляем конфигурационный файл парсера
        parser_config_path = Path('ParserQ/config.json')
        if parser_config_path.exists():
            with open(parser_config_path, 'r', encoding='utf-8') as f:
                parser_config = json.load(f)
        else:
            parser_config = {}
        
        # Обновляем настройки парсера
        if 'api_id' in new_settings:
            parser_config['api_id'] = new_settings['api_id']
        if 'api_hash' in new_settings:
            parser_config['api_hash'] = new_settings['api_hash']
        if 'phone_number' in new_settings:
            parser_config['phone_number'] = new_settings['phone_number']
        if 'group_ids' in new_settings:
            # Конвертируем группы в нужный формат для парсера
            parser_config['group_ids'] = []
            for group in new_settings['group_ids']:
                if isinstance(group, dict):
                    # Новый формат: {'id': '-123', 'name': 'Group Name'}
                    try:
                        parser_config['group_ids'].append(int(group['id']))
                    except (ValueError, KeyError):
                        # Если не удалось сконвертировать, пропускаем
                        pass
                else:
                    # Старый формат: просто ID как строка
                    try:
                        parser_config['group_ids'].append(int(group))
                    except ValueError:
                        # Если не удалось сконвертировать, пропускаем
                        pass
            
            # Также обновляем group_types для парсера
            parser_group_types = {}
            for i, group in enumerate(new_settings['group_ids']):
                if isinstance(group, dict):
                    group_id = group['id']
                else:
                    group_id = group
                
                # Простое распределение: первая группа - расходы, вторая - доходы
                group_type = 'expense' if i == 0 else 'income' if i == 1 else 'other'
                parser_group_types[group_id] = group_type
            
            parser_config['group_types'] = parser_group_types
        
        # Сохраняем обновленный конфиг парсера
        with open(parser_config_path, 'w', encoding='utf-8') as f:
            json.dump(parser_config, f, indent=4, ensure_ascii=False)
        
        # Очищаем данные транзакций в директории ParserQ
        transactions_file = Path('ParserQ/transactions.json')
        if transactions_file.exists():
            # Создаем пустую структуру
            empty_data = {"income": [], "expense": [], "last_updated": datetime.now().isoformat()}
            with open(transactions_file, 'w', encoding='utf-8') as f:
                json.dump(empty_data, f, indent=2, ensure_ascii=False)
        
        # Обновляем состояние приложения
        financial_app.transactions = []
        financial_app.last_update = datetime.now()  # type: ignore
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully and data cleared'
        })
    
    except Exception as e:
        logger.error(f"Error in api_settings_post: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/update', methods=['POST'])
def api_force_update():
    """Force data update"""
    try:
        # Запускаем обновление данных в фоновом режиме
        def run_parser():
            try:
                # Запускаем парсер из директории ParserQ
                import subprocess
                import os
                
                parser_dir = os.path.join(os.getcwd(), 'ParserQ')
                if os.path.exists(parser_dir):
                    result = subprocess.run(
                        ['python', 'fetch_telegram_data.py'], 
                        cwd=parser_dir,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        logger.info("Parser executed successfully")
                        # После успешного выполнения парсера, перезагружаем данные в приложении
                        financial_app.load_existing_data()
                        # Обновляем время последнего обновления
                        financial_app.last_update = datetime.now()  # type: ignore
                    else:
                        logger.error(f"Parser execution failed: {result.stderr}")
                else:
                    logger.error("ParserQ directory not found")
            except Exception as e:
                logger.error(f"Error running parser: {e}")
        
        # Запускаем парсер в отдельном потоке
        import threading
        parser_thread = threading.Thread(target=run_parser)
        parser_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Update started in background'
        })
    except Exception as e:
        logger.error(f"Error in api_force_update: {e}")
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

@app.route('/api/clear-data', methods=['POST'])
def api_clear_data():
    """Clear all transaction data"""
    try:
        # Clear transactions file in ParserQ directory
        parser_transactions_file = Path('ParserQ/transactions.json')
        if parser_transactions_file.exists():
            # Create empty structure
            empty_data = {"income": [], "expense": [], "last_updated": datetime.now().isoformat()}
            with open(parser_transactions_file, 'w', encoding='utf-8') as f:
                json.dump(empty_data, f, indent=2, ensure_ascii=False)
        
        # Update app state
        financial_app.transactions = []
        financial_app.last_update = datetime.now()  # type: ignore
        
        return jsonify({
            'success': True,
            'message': 'Все данные успешно очищены'
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
    print("Please ensure your config.json has valid Telegram API credentials")
    run_app(host, port, debug)