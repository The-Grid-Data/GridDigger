"""
GridDigger Telegram Bot - Enhanced Main Application
"""
import logging
import sys
import signal
import time
import asyncio
from telegram.ext import Application, ContextTypes
from telegram.error import NetworkError, Forbidden
from telegram import Update

# Import enhanced modules
from config import Config
from logging_config import setup_logging, get_logger
from handlers.setup import setup
from cache import warm_cache, get_cache_stats
from database_v2 import get_database_health
# GraphQL tester removed - functionality consolidated

# Initialize logging first
logger = get_logger(__name__)


class BotApplication:
    """Main bot application with enhanced error handling and monitoring"""
    
    def __init__(self):
        self.application = None
        self.running = False
        
        # Validate configuration
        try:
            Config.validate()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            sys.exit(1)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def health_check(self):
        """Perform application health check"""
        logger.info("Performing health check...")
        
        # Check database health
        db_health = get_database_health()
        if db_health['status'] != 'healthy':
            logger.error(f"Database health check failed: {db_health}")
            return False
        
        logger.info(f"Database health: OK (response time: {db_health['response_time_ms']}ms)")
        
        # Check cache health
        cache_stats = get_cache_stats()
        logger.info(f"Cache status: {cache_stats}")
        
        return True
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced error handler with detailed logging"""
        logger.error(f"Update {update} caused error {context.error}")
        
        # Log additional context
        if update:
            user_id = update.effective_user.id if update.effective_user else "Unknown"
            chat_id = update.effective_chat.id if update.effective_chat else "Unknown"
            message_text = update.message.text if update.message else "No message"
            
            logger.error(f"Error context - User: {user_id}, Chat: {chat_id}, Message: {message_text}")
        
        # Handle specific error types
        if isinstance(context.error, NetworkError):
            logger.error("Network error occurred, bot will continue running")
        elif isinstance(context.error, Forbidden):
            logger.error("Forbidden error - bot token may be invalid")
        else:
            logger.exception("Unexpected error occurred")
    
    def initialize_bot(self):
        """Initialize bot with enhanced configuration"""
        try:
            logger.info("Initializing Telegram bot...")
            
            # Create application with enhanced settings
            self.application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
            
            # Setup handlers
            setup(self.application)
            
            # Add error handler
            self.application.add_error_handler(self.error_handler)
            
            logger.info("Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False
    
    async def start_bot(self):
        """Start the bot with appropriate mode"""
        try:
            if Config.MODE == "webhook":
                await self._start_webhook_mode()
            else:
                await self._start_polling_mode()
            
            self.running = True
            logger.info("Bot started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
    
    async def _start_webhook_mode(self):
        """Start bot in webhook mode"""
        logger.info(f"Starting webhook mode on port {Config.PORT}")
        
        await self.application.bot.set_webhook(
            url=f"{Config.WEBHOOK_URL}/{Config.TELEGRAM_TOKEN}",
            drop_pending_updates=True
        )
        
        # Start the application
        await self.application.initialize()
        await self.application.start()
        
        logger.info(f"Webhook started at {Config.WEBHOOK_URL}/{Config.TELEGRAM_TOKEN}")
    
    async def _start_polling_mode(self):
        """Start bot in polling mode"""
        logger.info("Starting polling mode")
        
        # Initialize and start the application
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)
        
        logger.info("Polling started")
    
    async def run(self):
        """Main run method"""
        try:
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Perform health check
            if not self.health_check():
                logger.error("Health check failed, exiting...")
                sys.exit(1)
            
            # Basic GraphQL connectivity test
            logger.info("🧪 Testing GraphQL connectivity...")
            try:
                import api_v2
                # Simple connectivity test
                test_result = api_v2.search_profiles_v2("test")
                if test_result is not None:
                    logger.info("✅ GraphQL endpoint is accessible")
                else:
                    logger.warning("⚠️ GraphQL endpoint returned no data for test query")
            except Exception as e:
                logger.warning(f"GraphQL connectivity test failed: {e}")
                logger.warning("Continuing startup, but GraphQL functionality may be impaired")
            
            # Warm up cache
            if Config.ENABLE_CACHING:
                logger.info("Warming up cache...")
                warm_cache()
            
            # Initialize and start bot
            if not self.initialize_bot():
                logger.error("Bot initialization failed, exiting...")
                sys.exit(1)
            
            await self.start_bot()
            
            # Keep the bot running
            print("\n🤖 Bot is running successfully!")
            print("📱 Send messages to your bot to test functionality")
            print("🛑 Press Ctrl+C to stop the bot\n")
            logger.info("Bot is running. Press Ctrl+C to stop.")
            
            # Keep running until interrupted
            try:
                while self.running:
                    await asyncio.sleep(0.1)  # Shorter sleep for more responsive shutdown
            except asyncio.CancelledError:
                logger.info("Bot execution cancelled")
            
        except KeyboardInterrupt:
            print("\n🛑 Shutdown signal received...")
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            raise
        finally:
            print("🔄 Shutting down bot...")
            await self.shutdown()
            print("✅ Bot shutdown complete")
    
    async def shutdown(self):
        """Graceful shutdown"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Shutting down bot...")
        
        try:
            if self.application:
                # Stop the updater first
                if hasattr(self.application, 'updater') and self.application.updater:
                    await self.application.updater.stop()
                    logger.debug("Updater stopped")
                
                # Stop the application
                await self.application.stop()
                logger.debug("Application stopped")
                
                # Shutdown the application
                await self.application.shutdown()
                logger.debug("Application shutdown complete")
                
                logger.info("Bot stopped successfully")
            
            # Additional cleanup can be added here
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            logger.info("Shutdown complete")


def main():
    """Main entry point"""
    try:
        # Create and run the application
        app = BotApplication()
        asyncio.run(app.run())
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()