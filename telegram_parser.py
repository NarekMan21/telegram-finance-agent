# pyright: reportGeneralTypeIssues=false
# pyright: reportOptionalMemberAccess=false
import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, cast

from telethon import TelegramClient, events
from telethon.tl.types import Message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramFinancialParser:
    def __init__(self, config_path: str = 'config.json'):
        """Initialize Telegram Financial Parser"""
        self.config = self.load_config(config_path)
        self.client: Optional[TelegramClient] = None
        self.is_running = False
        self.session_file = 'telegram_session.session'
        self.transactions_file = 'transactions.json'
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {config_path} not found")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    async def initialize_client(self) -> bool:
        """Initialize Telegram client"""
        try:
            api_id = self.config.get('api_id')
            api_hash = self.config.get('api_hash')
            
            if not api_id or not api_hash:
                logger.error("API ID or Hash not found in config")
                return False
            
            client = TelegramClient(self.session_file, api_id, api_hash)
            
            # Start client
            phone_number = self.config.get('phone_number')
            if phone_number:
                await client.start(phone=phone_number)
            else:
                await client.start()
            
            # Verify authorization
            if not await client.is_user_authorized():
                logger.error("Client not authorized. Please check your phone number and verification code.")
                return False
            
            self.client = client
            logger.info("Telegram client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            return False
    
    def parse_financial_message(self, message: str, group_id: str) -> Optional[Dict]:
        """
        Parse financial information from message text based on group type configuration.
        
        Instead of automatically detecting income/expense from keywords, this method
        uses the group_types configuration to determine transaction type based on 
        the group the message came from.
        
        Args:
            message (str): The text message to parse
            group_id (str): The ID of the group the message came from
            
        Returns:
            Optional[Dict]: Parsed transaction data or None if not a financial message
        """
        if not message:
            return None
        
        message = message.lower().strip()
        
        # Get group types mapping from config
        group_types = self.config.get('group_types', {})
        
        # Determine transaction type based on group ID
        # Handle both string and integer group IDs
        transaction_type = None
        for config_group_id, config_type in group_types.items():
            # Convert both to strings for comparison
            if str(config_group_id) == str(group_id):
                transaction_type = config_type
                break
        
        # If group type is not configured, return None
        if not transaction_type:
            logger.debug(f"No transaction type configured for group {group_id}")
            return None
        
        # Extract amount - try multiple patterns to be more flexible
        import re
        
        # Pattern 1: Number with currency symbol (original pattern)
        amount_pattern1 = r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:₽|руб|RUB|р)'
        amount_match1 = re.search(amount_pattern1, message)
        
        # Pattern 2: Number at the end of message (for cases like "description 10000")
        amount_pattern2 = r'(\d+(?:,\d{3})*(?:\.\d{2})?)$'
        amount_match2 = re.search(amount_pattern2, message)
        
        # Pattern 3: Any number in the message (least specific)
        amount_pattern3 = r'(\d+(?:,\d{3})*(?:\.\d{2})?)'
        amount_match3 = re.search(amount_pattern3, message)
        
        amount_match = amount_match1 or amount_match2 or amount_match3
        
        if not amount_match:
            return None
        
        amount_str = amount_match.group(1).replace(',', '')
        try:
            amount = float(amount_str)
        except ValueError:
            return None
        
        # Extract category (basic implementation)
        category = self.extract_category(message)
        
        return {
            'amount': amount,
            'type': transaction_type,  # Use type from group configuration
            'description': message[:100],  # First 100 chars as description
            'category': category
        }
    
    def extract_category(self, message: str) -> str:
        """Extract category from message"""
        categories = {
            'еда': ['продукты', 'магазин', 'еда', 'ресторан', 'кафе', 'обед', 'ужин'],
            'транспорт': ['такси', 'метро', 'автобус', 'бензин', 'транспорт', 'поездка'],
            'жкх': ['коммуналка', 'жкх', 'свет', 'вода', 'газ', 'интернет', 'телефон'],
            'развлечения': ['кино', 'театр', 'концерт', 'отдых', 'путешествие', 'отпуск'],
            'здоровье': ['аптека', 'врач', 'медицина', 'лекарства', 'больница'],
            'одежда': ['одежда', 'обувь', 'магазин одежды', 'стиль'],
            'образование': ['курсы', 'обучение', 'университет', 'книги', 'учеба'],
            'работа': ['зарплата', 'аванс', 'премия', 'доход', 'бизнес']
        }
        
        message_lower = message.lower()
        for category, keywords in categories.items():
            if any(keyword in message_lower for keyword in keywords):
                return category
        
        return 'другое'
    
    async def fetch_messages_from_group(self, group_id: str, limit: int = 100) -> List[Dict]:
        """Fetch messages from a specific group"""
        transactions = []
        
        # Check if client is initialized
        if self.client is None:
            logger.error("Client not initialized")
            return transactions
        
        client = cast(TelegramClient, self.client)
        
        try:
            # Get entity (group) - handle both string and integer IDs
            if isinstance(group_id, str) and group_id.startswith('-'):
                # This is a negative ID (supergroup/channel)
                entity = await client.get_entity(int(group_id))
            elif isinstance(group_id, str):
                # This might be a username or positive ID as string
                try:
                    entity = await client.get_entity(int(group_id))
                except ValueError:
                    # Try as username
                    entity = await client.get_entity(group_id)
            else:
                # This is already an integer
                entity = await client.get_entity(group_id)
            
            # Fetch recent messages
            async for message in client.iter_messages(entity, limit=limit):
                if message.text:
                    parsed_data = self.parse_financial_message(message.text, group_id)
                    
                    if parsed_data:
                        transaction = {
                            'id': str(message.id),  # This is the correct ID
                            'amount': parsed_data['amount'],
                            'type': parsed_data['type'],
                            'description': parsed_data['description'],
                            'category': parsed_data['category'],
                            'date': message.date.isoformat(),
                            'group_id': group_id,
                            'group_name': getattr(entity, 'title', 'Unknown Group'),
                            'message_id': message.id,
                            'raw_message': message.text[:200]  # First 200 chars
                        }
                        
                        transactions.append(transaction)
                        
                        logger.info(f"Found transaction: {transaction['type']} {transaction['amount']}₽ - {transaction['description'][:50]}...")
            
            logger.info(f"Fetched {len(transactions)} transactions from group {group_id}")
            
        except Exception as e:
            logger.error(f"Error fetching messages from group {group_id}: {e}")
        
        return transactions
    
    def save_transactions(self, transactions: List[Dict]):
        """Save transactions to JSON file in ParserQ format (separate income and expense arrays)"""
        try:
            # Load existing transactions
            existing_data = {
                'income': [],
                'expense': [],
                'last_updated': datetime.now().isoformat()
            }
            
            if os.path.exists(self.transactions_file):
                try:
                    with open(self.transactions_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except Exception as e:
                    logger.warning(f"Error loading existing transactions file: {e}")
                    # If there's an error loading the file, we'll start with empty arrays
            
            # Convert existing transactions to the new format if needed
            if isinstance(existing_data, list):
                # Old format - convert to new format
                income_transactions = [t for t in existing_data if t.get('type') == 'income']
                expense_transactions = [t for t in existing_data if t.get('type') == 'expense']
                existing_data = {
                    'income': income_transactions,
                    'expense': expense_transactions,
                    'last_updated': datetime.now().isoformat()
                }
            
            # Ensure we have the right structure
            if 'income' not in existing_data:
                existing_data['income'] = []
            if 'expense' not in existing_data:
                existing_data['expense'] = []
            
            # Create sets of existing transaction IDs for quick lookup
            # Use the correct ID field for comparison
            existing_income_ids = {str(item.get('id')) for item in existing_data['income']}
            existing_expense_ids = {str(item.get('id')) for item in existing_data['expense']}
            
            # Separate new transactions by type and filter out duplicates
            new_income = []
            new_expense = []
            
            for t in transactions:
                # Use the correct ID field - 'id' in the transaction object
                transaction_id = str(t.get('id'))
                transaction_type = t.get('type')
                
                # Only add transaction if it doesn't already exist
                if transaction_type == 'income' and transaction_id not in existing_income_ids:
                    new_income.append(t)
                elif transaction_type == 'expense' and transaction_id not in existing_expense_ids:
                    new_expense.append(t)
            
            # Convert to ParserQ format
            def convert_to_parserq_format(transaction_list):
                converted = []
                for t in transaction_list:
                    converted_item = {
                        'id': str(t.get('id')),  # Use 'id' field directly
                        'timestamp': t.get('date', datetime.now().isoformat()),
                        'group_id': t.get('group_id'),
                        'group_title': t.get('group_name', 'Unknown'),
                        'text': t.get('raw_message', t.get('description', '')),
                        'sender_id': 0,  # We don't have sender info in the new format
                        'amount': t.get('amount', 0),
                        'currency': 'RUB',
                        'description': t.get('description', '')
                    }
                    converted.append(converted_item)
                return converted
            
            # Convert new transactions
            converted_new_income = convert_to_parserq_format(new_income)
            converted_new_expense = convert_to_parserq_format(new_expense)
            
            # Merge with existing data (add new transactions to the beginning)
            # Only add new transactions, don't duplicate existing ones
            existing_data['income'] = converted_new_income + existing_data['income']
            existing_data['expense'] = converted_new_expense + existing_data['expense']
            
            # Update last_updated timestamp
            existing_data['last_updated'] = datetime.now().isoformat()
            
            # Save to file
            with open(self.transactions_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved {len(converted_new_income)} new income and {len(converted_new_expense)} new expense transactions. Total: {len(existing_data['income'])} income, {len(existing_data['expense'])} expense")
            
        except Exception as e:
            logger.error(f"Error saving transactions: {e}")
    
    async def start_parsing(self):
        """Start parsing messages from configured groups"""
        if not await self.initialize_client():
            return False
        
        self.is_running = True
        group_ids = self.config.get('group_ids', [])
        
        if not group_ids:
            logger.error("No group IDs configured")
            return False
        
        logger.info(f"Starting to parse messages from {len(group_ids)} groups")
        
        all_transactions = []
        
        # Handle both old format (list of strings) and new format (list of objects)
        for group_item in group_ids:
            if not self.is_running:
                break
            
            # Extract group ID from either old format (string) or new format (object)
            if isinstance(group_item, dict):
                group_id = group_item.get('id')
                group_name = group_item.get('name', 'Unknown')
            else:
                group_id = group_item
                group_name = 'Unknown'
            
            if not group_id:
                logger.warning(f"Skipping invalid group item: {group_item}")
                continue
            
            logger.info(f"Processing group: {group_id} ({group_name})")
            transactions = await self.fetch_messages_from_group(group_id)
            all_transactions.extend(transactions)
        
        if all_transactions:
            self.save_transactions(all_transactions)
            logger.info(f"Parsing completed. Found {len(all_transactions)} transactions total")
        else:
            logger.info("No financial transactions found in the groups")
        
        if self.client:
            client = cast(TelegramClient, self.client)
            await client.disconnect()
        return True
    
    async def start_real_time_monitoring(self):
        """Start real-time monitoring of groups"""
        if not await self.initialize_client():
            return False
        
        # Check if client is initialized
        if self.client is None:
            logger.error("Client not initialized")
            return False
        
        client = cast(TelegramClient, self.client)
        self.is_running = True
        
        # Get group IDs in the correct format for monitoring
        group_ids = self.config.get('group_ids', [])
        chat_ids = []
        
        # Extract chat IDs from either old format (strings) or new format (objects)
        for group_item in group_ids:
            if isinstance(group_item, dict):
                group_id = group_item.get('id')
            else:
                group_id = group_item
            
            if group_id:
                try:
                    # Convert to integer for Telethon
                    chat_ids.append(int(group_id))
                except ValueError:
                    logger.warning(f"Invalid group ID format: {group_id}")
        
        if not chat_ids:
            logger.error("No valid group IDs found for monitoring")
            return False
        
        @client.on(events.NewMessage(chats=chat_ids))
        async def handle_new_message(event):
            message = event.message
            
            if message.text:
                # Get the correct group ID as string
                group_id = str(event.chat_id)
                parsed_data = self.parse_financial_message(message.text, group_id)
                
                if parsed_data:
                    transaction = {
                        'id': str(message.id),  # This is the correct ID
                        'amount': parsed_data['amount'],
                        'type': parsed_data['type'],
                        'description': parsed_data['description'],
                        'category': parsed_data['category'],
                        'date': message.date.isoformat(),
                        'group_id': group_id,
                        'group_name': getattr(event.chat, 'title', 'Unknown Group'),
                        'message_id': message.id,
                        'raw_message': message.text[:200]
                    }
                    
                    # Save single transaction
                    self.save_transactions([transaction])
                    
                    logger.info(f"New transaction detected: {transaction['type']} {transaction['amount']}₽")
        
        logger.info("Starting real-time monitoring...")
        await client.run_until_disconnected()
        
        return True
    
    def stop(self):
        """Stop the parser"""
        self.is_running = False
        if self.client:
            client = cast(TelegramClient, self.client)
            client.disconnect()

def main():
    """Main function for standalone usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Telegram Financial Parser')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--real-time', action='store_true', help='Enable real-time monitoring')
    parser.add_argument('--once', action='store_true', help='Parse once and exit')
    
    args = parser.parse_args()
    
    # Create parser instance
    parser_instance = TelegramFinancialParser(args.config)
    
    async def run():
        if args.real_time:
            await parser_instance.start_real_time_monitoring()
        elif args.once:
            await parser_instance.start_parsing()
        else:
            await parser_instance.start_parsing()
    
    # Run the async function
    asyncio.run(run())

if __name__ == '__main__':
    main()