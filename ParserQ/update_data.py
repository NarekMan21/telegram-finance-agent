import subprocess
import time
import logging
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def update_data():
    """Update data from Telegram"""
    try:
        logger.info("Updating data from Telegram...")
        
        # Run the fetch script
        result = subprocess.run(['python', 'fetch_telegram_data.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            logger.info("Data updated successfully")
        else:
            logger.error(f"Error updating data: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Error updating data: {e}")

if __name__ == '__main__':
    while True:
        update_data()
        # Wait 30 seconds before next update
        time.sleep(30)