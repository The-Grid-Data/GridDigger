"""
Webhook server for GridDigger Telegram Bot on Railway
"""
import asyncio
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application
import json

from config import Config
from logging_config import setup_logging, get_logger
from handlers.setup import setup

# Initialize logging
logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global bot application
bot_application = None

async def initialize_bot():
    """Initialize the Telegram bot application"""
    global bot_application
    
    try:
        logger.info("Initializing Telegram bot for webhook mode...")
        
        # Create application
        bot_application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        
        # Setup handlers
        setup(bot_application)
        
        # Initialize the application
        await bot_application.initialize()
        await bot_application.start()
        
        # Set webhook
        webhook_url = f"{Config.WEBHOOK_URL}/{Config.TELEGRAM_TOKEN}"
        await bot_application.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        
        logger.info(f"Bot initialized successfully with webhook: {webhook_url}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        return False

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'GridDigger Telegram Bot',
        'webhook_configured': bool(bot_application)
    })

@app.route(f'/{Config.TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming webhook requests from Telegram"""
    global bot_application
    
    if not bot_application:
        logger.error("Bot application not initialized")
        return jsonify({'error': 'Bot not initialized'}), 500
    
    try:
        # Get the update from Telegram
        update_data = request.get_json()
        
        if not update_data:
            logger.warning("Received empty update data")
            return jsonify({'status': 'ok'})
        
        logger.debug(f"Received update: {update_data}")
        
        # Create Update object
        update = Update.de_json(update_data, bot_application.bot)
        
        if update:
            # Process the update in a new event loop
            def process_update_sync():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(bot_application.process_update(update))
                finally:
                    loop.close()
            
            # Run in a separate thread to avoid blocking Flask
            import threading
            thread = threading.Thread(target=process_update_sync)
            thread.start()
            
            logger.debug(f"Processing update {update.update_id}")
        else:
            logger.warning("Failed to create Update object from received data")
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Manually set webhook (for debugging)"""
    global bot_application
    
    if not bot_application:
        return jsonify({'error': 'Bot not initialized'}), 500
    
    try:
        webhook_url = f"{Config.WEBHOOK_URL}/{Config.TELEGRAM_TOKEN}"
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _set_webhook():
            await bot_application.bot.set_webhook(
                url=webhook_url,
                drop_pending_updates=True
            )
        
        loop.run_until_complete(_set_webhook())
        loop.close()
        
        logger.info(f"Webhook set to: {webhook_url}")
        return jsonify({'status': 'webhook set', 'url': webhook_url})
        
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'error': str(e)}), 500

def create_app():
    """Create and configure the Flask app"""
    # Initialize bot on startup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    success = loop.run_until_complete(initialize_bot())
    
    if not success:
        logger.error("Failed to initialize bot, exiting...")
        exit(1)
    
    logger.info(f"Webhook server starting on port {Config.PORT}")
    return app

if __name__ == '__main__':
    # Validate configuration
    try:
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        exit(1)
    
    # Create app
    flask_app = create_app()
    
    # Run the Flask app
    flask_app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=False
    )