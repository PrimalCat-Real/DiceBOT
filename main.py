import asyncio
import discord
import os
import signal
from dotenv import load_dotenv

from bot.discord_bot import DiscordBot
from bot.telegram_bot import TelegramBot
from database.database import DatabaseManager
from logs import logging_config

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
connection_string = os.getenv("MONGODB")

logger = logging_config.setup_logging()

database_name = 'dice_bot_db'
db_manager = DatabaseManager(connection_string, database_name)

discord_bot = None

async def run_discord_bot():
    global discord_bot
    intents = discord.Intents.default()
    intents.message_content = True
    discord_bot = DiscordBot(token=DISCORD_TOKEN, intents=intents, logger=logger, database_manager=db_manager)
    await discord_bot.run_bot()

async def main():
    discord_task = asyncio.create_task(run_discord_bot())
    try:
        await discord_task
    except KeyboardInterrupt:
        logger.info("Main process interrupted by keyboard.")
        discord_task.cancel()
        await discord_task
    except Exception as e:
        logger.exception(f"Error in main: {e}")
    finally:
        logger.info("Application finished.")

def signal_handler(sig, frame):
    logger.info("Received signal. Shutting down...")
    if discord_bot:
        discord_bot.close()
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Main process interrupted by keyboard.")
    finally:
        logger.info("Application finished.")