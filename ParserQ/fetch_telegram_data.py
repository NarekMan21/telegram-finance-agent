import asyncio
import json
import logging
import os
from datetime import datetime
from telethon import TelegramClient

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

API_ID = 0
API_HASH = ''
PHONE_NUMBER = '+1234567890'
GROUP_IDS = [
    -1001234567890,
    -1000987654321,
]
CONFIG_FILE = 'config.json'
DATA_FILE = 'transactions.json'
income_messages = []
expense_messages = []

def load_config():
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
    data = {
        'income': income_messages,
        'expense': expense_messages,
        'last_updated': datetime.now().isoformat()
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Data saved to {DATA_FILE}")

def process_message(message_data: dict, chat) -> dict:
    return {
        'id': message_data['message_id'],
        'timestamp': message_data['timestamp'],
        'group_id': message_data['group_id'],
        'group_title': getattr(chat, 'title', 'Unknown'),
        'text': message_data['message_text'],
        'sender_id': message_data['sender_id'],
        'amount': extract_amount(message_data['message_text']),
        'currency': extract_currency(message_data['message_text']),
        'description': message_data['message_text'][:100]
    }

def extract_amount(text: str) -> float:
    import re
    amounts = re.findall(r'\d+(?:\.\d+)?', text)
    return float(max(amounts, key=float)) if amounts else 0.0

def extract_currency(text: str) -> str:
    for symbol in ['₽', '$', '€', 'USD', 'EUR', 'RUB']:
        if symbol in text:
            return symbol
    return 'RUB'

async def fetch_messages():
    global income_messages, expense_messages
    load_config()
    if not API_ID or not API_HASH:
        logger.error("Update api_id and api_hash in config.json before first run")
        return
    client = TelegramClient('my_session', API_ID, API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            logger.error("Not authorized. Please run parser.py first to authenticate.")
            return
        logger.info("Fetching messages from Telegram...")
        income_messages.clear()
        expense_messages.clear()
        income_group_id = -4855539306
        expense_group_id = -4884869527
        for group_id in GROUP_IDS:
            try:
                chat = await client.get_entity(group_id)
                async for message in client.iter_messages(group_id, limit=100):
                    if message.text:
                        message_data = {
                            'timestamp': message.date.isoformat() if message.date else datetime.now().isoformat(),
                            'group_id': group_id,
                            'group_title': getattr(chat, 'title', 'Unknown'),
                            'sender_id': message.sender_id,
                            'message_id': message.id,
                            'message_text': message.text,
                            'is_reply': message.reply_to_msg_id is not None,
                        }
                        processed_message = process_message(message_data, chat)
                        if group_id == income_group_id:
                            income_messages.append(processed_message)
                        elif group_id == expense_group_id:
                            expense_messages.append(processed_message)
            except Exception as e:
                logger.error(f"Error fetching messages from group {group_id}: {e}")
        logger.info(f"Fetched {len(income_messages)} income messages and {len(expense_messages)} expense messages")
        save_data()
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(fetch_messages())
