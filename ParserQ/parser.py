import asyncio
import logging
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import os
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("messages.log"),
        logging.StreamHandler()
    ]
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

# Number of days of history to fetch
HISTORY_DAYS = 30

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

def save_config():
    """Save current configuration to file"""
    config = {
        'api_id': API_ID,
        'api_hash': API_HASH,
        'phone_number': PHONE_NUMBER,
        'group_ids': GROUP_IDS
    }
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info("Configuration saved to config.json")
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")

# Initialize the client
client = TelegramClient('my_session', API_ID, API_HASH)

async def fetch_history():
    """Fetch and log historical messages from monitored groups"""
    logger.info(f"Fetching historical messages for the last {HISTORY_DAYS} days...")
    
    # Calculate the date from which to fetch messages
    since_date = datetime.now() - timedelta(days=HISTORY_DAYS)
    
    for group_id in GROUP_IDS:
        try:
            logger.info(f"Fetching history for group {group_id}...")
            
            # Get the chat entity
            chat = await client.get_entity(group_id)
            
            # Fetch messages
            async for message in client.iter_messages(
                entity=group_id, 
                reverse=True,  # From oldest to newest
                offset_date=since_date
            ):
                # Log message details
                log_entry = {
                    'timestamp': message.date.isoformat() if message.date else datetime.now().isoformat(),
                    'group_id': group_id,
                    'group_title': getattr(chat, 'title', 'Unknown'),
                    'sender_id': message.sender_id,
                    'message_id': message.id,
                    'message_text': message.text,
                    'is_reply': message.reply_to_msg_id is not None,
                }
                
                # Log to file
                logger.info(f"Historical message in {getattr(chat, 'title', 'Unknown')} ({group_id}): {message.text}")
                
        except Exception as e:
            logger.error(f"Error fetching history for group {group_id}: {e}")

@client.on(events.NewMessage(chats=GROUP_IDS))
async def handle_new_message(event):
    """Handle new messages in monitored groups"""
    try:
        # Extract message details
        message = event.message
        chat = await event.get_chat()
        
        # Log message details
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'group_id': chat.id,
            'group_title': getattr(chat, 'title', 'Unknown'),
            'sender_id': message.sender_id,
            'message_id': message.id,
            'message_text': message.text,
            'is_reply': message.reply_to_msg_id is not None,
        }
        
        # Log to file
        logger.info(f"New message in {getattr(chat, 'title', 'Unknown')} ({chat.id}): {message.text}")
        
        # Here you could add additional processing like:
        # - Parsing expense/income amounts
        # - Saving to database
        # - Sending notifications
        # - etc.
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")

async def main():
    """Main function to start the parser"""
    # Load configuration
    load_config()
    
    # Validate phone number
    if PHONE_NUMBER == '+1234567890' or not PHONE_NUMBER.startswith('+'):
        logger.error("Пожалуйста, обновите номер телефона в config.json")
        logger.error("Номер телефона должен начинаться с '+' и содержать код страны")
        return
    
    # Connect to Telegram
    await client.connect()
    
    # Check if authorized
    if not await client.is_user_authorized():
        try:
            # Send code request
            await client.send_code_request(PHONE_NUMBER)
            
            try:
                # Get the code from user input
                code = input('Введите код, который вы получили: ')
                await client.sign_in(PHONE_NUMBER, code)
                
                # Save configuration after successful login
                save_config()
            except SessionPasswordNeededError:
                # Handle 2FA
                password = input('Включена двухфакторная аутентификация. Пожалуйста, введите ваш пароль: ')
                await client.sign_in(password=password)
        except Exception as e:
            logger.error(f"Ошибка авторизации: {e}")
            logger.error("Пожалуйста, проверьте правильность номера телефона в config.json")
            return
    
    # Fetch historical messages
    await fetch_history()
    
    logger.info("Подключение к Telegram установлено. Наблюдение за группами...")
    
    # Run the client until disconnected
    client.run_until_disconnected()

if __name__ == "__main__":
    try:
        # Create and run the event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
    except Exception as e:
        logger.error(f"Необработанная ошибка: {e}")