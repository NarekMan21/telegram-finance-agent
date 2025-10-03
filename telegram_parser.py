# pyright: reportGeneralTypeIssues=false
# pyright: reportOptionalMemberAccess=false
#!/usr/bin/env python3
"""
Telegram Financial Parser
Parses financial messages from Telegram groups
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramFinancialParser:
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = self.load_config(config_path)
        self.client = None
        
        # Extract configuration values with environment variable fallback
        self.api_id = os.environ.get('API_ID') or self.config.get('api_id')
        self.api_hash = os.environ.get('API_HASH') or self.config.get('api_hash')
        self.phone_number = os.environ.get('PHONE_NUMBER') or self.config.get('phone_number')
        self.group_ids = self._parse_group_ids(os.environ.get('GROUP_IDS') or self.config.get('group_ids', []))
        self.group_types = self._parse_group_types(os.environ.get('GROUP_TYPES') or self.config.get('group_types', {}))
        
        # Validate required configuration
        if not all([self.api_id, self.api_hash, self.phone_number]):
            raise ValueError("Missing required configuration: API_ID, API_HASH, and PHONE_NUMBER must be set")
    
    def _parse_group_ids(self, group_ids):
        """Parse group IDs from environment variable or config"""
        if isinstance(group_ids, str):
            # If it's a string (from environment variable), parse as JSON or comma-separated
            try:
                return json.loads(group_ids)
            except json.JSONDecodeError:
                # Try comma-separated values
                return [gid.strip() for gid in group_ids.split(',') if gid.strip()]
        return group_ids
    
    def _parse_group_types(self, group_types):
        """Parse group types from environment variable or config"""
        if isinstance(group_types, str):
            # If it's a string (from environment variable), parse as JSON
            try:
                return json.loads(group_types)
            except json.JSONDecodeError:
                # If parsing fails, return empty dict
                return {}
        return group_types
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from file or return empty dict if not found"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file {config_path} not found, using environment variables or defaults")
                return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def initialize_client(self):
        """Initialize Telegram client"""
        if not self.client:
            self.client = TelegramClient('telegram_session', self.api_id, self.api_hash)
            await self.client.start()
    
    async def authenticate_user(self):
        """Authenticate user if needed"""
        if not self.client:
            await self.initialize_client()
            
        if await self.client.is_user_authorized():
            logger.info("User already authorized")
        else:
            logger.info("Sending code request...")
            await self.client.send_code_request(self.phone_number)
            code = input("Enter the code you received: ")
            try:
                await self.client.sign_in(self.phone_number, code)
            except SessionPasswordNeededError:
                password = input("Two-step verification is enabled. Please enter your password: ")
                await self.client.sign_in(password=password)
    
    async def parse_group_messages(self, group_id: str, limit: int = 100) -> List[Dict]:
        """Parse messages from a specific group"""
        if not self.client:
            await self.initialize_client()
        
        try:
            # Get group entity
            entity = await self.client.get_entity(int(group_id))
            
            # Get message history
            history = await self.client(GetHistoryRequest(
                peer=entity,
                offset_id=0,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            
            transactions = []
            for message in history.messages:
                if message.message:
                    # Parse financial transactions from message
                    transaction = self.parse_financial_message(message.message, group_id)
                    if transaction:
                        transaction['id'] = str(message.id)
                        transaction['timestamp'] = message.date.isoformat() if message.date else datetime.now().isoformat()
                        transaction['group_id'] = group_id
                        transaction['group_name'] = entity.title
                        transactions.append(transaction)
            
            return transactions
        except Exception as e:
            logger.error(f"Error parsing group {group_id}: {e}")
            return []
    
    def parse_financial_message(self, message: str, group_id: str) -> Optional[Dict]:
        """Parse financial information from a message"""
        # This is a simplified parser - you may want to enhance this based on your message format
        message = message.lower()
        
        # Try to extract amount (assuming it's a number possibly with currency symbols)
        import re
        amount_pattern = r'(\d+[.,]?\d*)'
        amounts = re.findall(amount_pattern, message)
        
        if amounts:
            # Convert to float (taking the first amount found)
            amount_str = amounts[0].replace(',', '.')
            try:
                amount = float(amount_str)
                
                # Determine transaction type based on group configuration
                transaction_type = self.group_types.get(str(group_id), 'expense')
                
                return {
                    'amount': amount,
                    'type': transaction_type,
                    'text': message,
                    'description': self.extract_description(message)
                }
            except ValueError:
                pass
        
        return None
    
    def extract_description(self, message: str) -> str:
        """Extract description from message"""
        # Simple extraction - you may want to enhance this
        words = message.split()
        if len(words) > 10:
            return ' '.join(words[:10]) + '...'
        return message
    
    async def start_parsing(self, limit_per_group: int = 100) -> bool:
        """Start parsing all configured groups"""
        try:
            await self.authenticate_user()
            
            all_transactions = {
                'income': [],
                'expense': []
            }
            
            for group_id in self.group_ids:
                logger.info(f"Parsing group {group_id}...")
                transactions = await self.parse_group_messages(group_id, limit_per_group)
                
                # Categorize transactions
                for transaction in transactions:
                    if transaction['type'] == 'income':
                        all_transactions['income'].append(transaction)
                    else:
                        all_transactions['expense'].append(transaction)
            
            # Save transactions to file
            self.save_transactions(all_transactions)
            
            logger.info(f"Parsing completed. Found {len(all_transactions['income'])} income and {len(all_transactions['expense'])} expense transactions")
            return True
            
        except Exception as e:
            logger.error(f"Error during parsing: {e}")
            return False
    
    def save_transactions(self, transactions: Dict):
        """Save transactions to file"""
        try:
            with open('transactions.json', 'w', encoding='utf-8') as f:
                json.dump(transactions, f, indent=2, ensure_ascii=False)
            logger.info("Transactions saved successfully")
        except Exception as e:
            logger.error(f"Error saving transactions: {e}")

# Example usage
if __name__ == "__main__":
    parser = TelegramFinancialParser()
    asyncio.run(parser.start_parsing())
