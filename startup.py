#!/usr/bin/env python3
"""
Startup script for Telegram Financial Agent
Checks environment variables and starts the application
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = ['API_ID', 'API_HASH', 'PHONE_NUMBER']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set the following environment variables:")
        logger.info("  - API_ID: Your Telegram API ID")
        logger.info("  - API_HASH: Your Telegram API Hash")
        logger.info("  - PHONE_NUMBER: Your phone number")
        return False
    
    # Check if GROUP_IDS is set
    group_ids = os.environ.get('GROUP_IDS')
    if not group_ids:
        logger.warning("GROUP_IDS environment variable not set, using empty list")
    
    # Check if GROUP_TYPES is set
    group_types = os.environ.get('GROUP_TYPES')
    if not group_types:
        logger.warning("GROUP_TYPES environment variable not set, using empty dict")
    
    return True

def main():
    """Main startup function"""
    logger.info("Starting Telegram Financial Agent startup script...")
    
    # Check environment variables
    if not check_environment_variables():
        logger.error("Environment variables check failed. Exiting...")
        sys.exit(1)
    
    # Import and start the main application
    try:
        logger.info("Starting Telegram Financial Agent...")
        from app import run_app
        
        # Get port from environment variable (Railway sets this)
        port = int(os.environ.get('PORT', 8080))
        
        logger.info(f"Running application on port {port}")
        run_app(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        logger.exception(e)
        sys.exit(1)

if __name__ == '__main__':
    main()