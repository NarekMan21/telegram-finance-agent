import asyncio
import json
import logging
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration - Replace with your actual values
API_ID = 20517386
API_HASH = '73457be44439ae991e7ba2bf97820a31'
PHONE_NUMBER = '+1234567890'  # Replace with your phone number

# Group IDs to monitor (replace with actual group IDs)
GROUP_IDS = [
    -1001234567890,  # Expense group
    -1000987654321,  # Income group
]

# Configuration file path
CONFIG_FILE = 'config.json'
DATA_FILE = 'transactions.json'

# Data storage
income_messages = []
expense_messages = []

def load_config():
    """Load configuration from file if it exists"""
    global API_ID, API_HASH, PHONE_NUMBER, GROUP_IDS
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                API_ID = config.get('api_id', API_ID)
                API_HASH = config.get('api_hash', API_HASH)
                PHONE_NUMBER = config.get('phone_number', PHONE_NUMBER)
                GROUP_IDS = config.get('group_ids', GROUP_IDS)
            logger.info("Configuration loaded from config.json")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")

def save_data():
    """Save data to file"""
    data = {
        'income': income_messages,
        'expense': expense_messages,
        'last_updated': datetime.now().isoformat()
    }
    
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Data saved to {DATA_FILE}")
    except Exception as e:
        logger.error(f"Error saving data: {e}")

def process_message(message_data: dict, chat) -> dict:
    """Process message and extract financial data"""
    # This is a simplified example - you would need to implement
    # more sophisticated parsing based on your message formats
    return {
        'id': message_data['message_id'],
        'timestamp': message_data['timestamp'],
        'group_id': message_data['group_id'],
        'group_title': getattr(chat, 'title', 'Unknown'),
        'text': message_data['message_text'],
        'sender_id': message_data['sender_id'],
        'amount': extract_amount(message_data['message_text']),
        'currency': extract_currency(message_data['message_text']),
        'description': message_data['message_text'][:100]  # First 100 characters
    }

def extract_amount(text: str) -> float:
    """Extract amount from message text"""
    # This is a simplified example - you would need to implement
    # more sophisticated parsing based on your message formats
    import re
    # Try to find numbers with optional decimal points
    amounts = re.findall(r'\d+(?:\.\d+)?', text)
    if amounts:
        # Return the largest number as the amount (assuming it's the main amount)
        return float(max(amounts, key=float))
    return 0.0

def extract_currency(text: str) -> str:
    """Extract currency from message text"""
    # This is a simplified example - you would need to implement
    # more sophisticated parsing based on your message formats
    currency_symbols = ['₽', '$', '€', 'USD', 'EUR', 'RUB']
    for symbol in currency_symbols:
        if symbol in text:
            return symbol
    return 'RUB'  # Default currency

async def fetch_messages():
    """Fetch messages from Telegram and classify them by group"""
    global income_messages, expense_messages
    
    # Load configuration
    load_config()
    
    # Initialize the client
    client = TelegramClient('my_session', API_ID, API_HASH)
    
    try:
        # Connect to Telegram
        await client.connect()
        
        # Check if authorized
        if not await client.is_user_authorized():
            logger.error("Not authorized. Please run parser.py first to authenticate.")
            return
        
        logger.info("Fetching messages from Telegram...")
        
        # Clear existing data
        income_messages.clear()
        expense_messages.clear()
        
        # Define group purposes (you can adjust these based on your actual group IDs)
        # Assuming:
        # -4855539306 is the INCOME group
        # -4884869527 is the EXPENSE group
        income_group_id = -4855539306
        expense_group_id = -4884869527
        
        # Fetch messages from all groups
        for group_id in GROUP_IDS:
            try:
                logger.info(f"Fetching messages from group {group_id}...")
                
                # Get the chat entity
                chat = await client.get_entity(group_id)
                
                # Fetch recent messages (last 100)
                async for message in client.iter_messages(group_id, limit=100):
                    if message.text:  # Only process messages with text
                        # Create message data structure
                        message_data = {
                            'timestamp': message.date.isoformat() if message.date else datetime.now().isoformat(),
                            'group_id': group_id,
                            'group_title': getattr(chat, 'title', 'Unknown'),
                            'sender_id': message.sender_id,
                            'message_id': message.id,
                            'message_text': message.text,
                            'is_reply': message.reply_to_msg_id is not None,
                        }
                        
                        # Process message
                        processed_message = process_message(message_data, chat)
                        
                        # Add to appropriate list based on group ID
                        if group_id == income_group_id:
                            income_messages.append(processed_message)
                            logger.info(f"Income message: {message.text[:50]}...")
                        elif group_id == expense_group_id:
                            expense_messages.append(processed_message)
                            logger.info(f"Expense message: {message.text[:50]}...")
                        else:
                            # For other groups, we can classify based on content or ignore
                            logger.info(f"Message from other group {group_id}: {message.text[:50]}...")
                            
            except Exception as e:
                logger.error(f"Error fetching messages from group {group_id}: {e}")
                
        logger.info(f"Fetched {len(income_messages)} income messages and {len(expense_messages)} expense messages")
        
        # Save data to file
        save_data()
        
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(fetch_messages())