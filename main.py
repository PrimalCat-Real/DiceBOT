import asyncio
import threading

import discord
from bot.discord_bot import DiscordBot
from bot.telegram_bot import TelegramBot

import os
from dotenv import load_dotenv

from database.database import DatabaseManager
from logs import logging_config

load_dotenv() 
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
connection_string = os.getenv("MONGODB")

logger = logging_config.setup_logging() 

database_name = 'dice_bot_db'

db_manager = DatabaseManager(connection_string, database_name)


async def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = DiscordBot(token=DISCORD_TOKEN, intents=intents, logger=logger, database_manager=db_manager)
    await bot.run_bot()

async def run_telegram_bot():
    bot = TelegramBot(token=TELEGRAM_TOKEN, logger=logger, database_manager=db_manager)
    await bot.run_bot()

async def main():
    try:
        await asyncio.gather(run_discord_bot(), run_telegram_bot())
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt. Shutting down...")
    finally:
        logger.info("Application finished.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Main process interrupted by keyboard.")