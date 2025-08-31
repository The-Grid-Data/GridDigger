"""
Webhook server for GridDigger Telegram Bot on Railway
"""
import asyncio
import logging
import threading
import queue
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

# Global bot application and event loop
bot_application = None
bot_loop = None
update_queue = queue.Queue()

def run_bot_loop():
    """Run the bot's event loop in a separate thread"""
    global bot_loop, bot_application
    
    bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bot_loop)
    
    async def process_updates():
        """Process updates from the queue"""
        while True:
            try:
                # Check for updates in the queue
                try:
                    update_data = update_queue.get(timeout=0.1)
                    update = Update.de_json(update_data, bot_application.bot)
                    if update:
                        await bot_application.process_update(update)
                        logger.debug(f"Processed update {update.update_id}")
                    update_queue.task_done()
                except queue.Empty:
                    pass
                except Exception as e:
                    logger.error(f"Error processing update: {e}")
                
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Error in update processing loop: {e}")
                await asyncio.sleep(1)  # Longer delay on error
    
    try:
        # Initialize bot in this loop
        bot_loop.run_until_complete(initialize_bot_async())
        # Start processing updates
        bot_loop.run_until_complete(process_updates())
    except Exception as e:
        logger.error(f"Error in bot loop: {e}")
    finally:
        if bot_loop and not bot_loop.is_closed():
            bot_loop.close()

async def initialize_bot_async():
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
        'webhook_configured': bool(bot_application),
        'bot_loop_running': bot_loop is not None and not bot_loop.is_closed()
    })

@app.route(f'/{Config.TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming webhook requests from Telegram"""
    global bot_application, update_queue
    
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
        
        # Add update to queue for processing
        update_queue.put(update_data)
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def create_app():
    """Create and configure the Flask app"""
    # Start the bot loop in a separate thread
    bot_thread = threading.Thread(target=run_bot_loop, daemon=True)
    bot_thread.start()
    
    # Give the bot time to initialize
    import time
    time.sleep(3)
    
    if not bot_application:
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
        debug=False,
        threaded=True
    )