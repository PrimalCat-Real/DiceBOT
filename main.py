import asyncio
import discord
import os
import signal
from dotenv import load_dotenv

from bot.discord_bot import DiscordBot
from bot.telegram_bot import TelegramBot
from database.database import DatabaseManager
from logs import logging_config

# completion = client.chat.completions.create(
#     model="gpt-4o",
#     store=True,
#     messages=[
#         {"role": "user", "content": "write a haiku about ai"}
#     ]
# )
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RCON_PORT = os.getenv("RCON_PORT")
RCON_HOST = os.getenv("RCON_HOST")
RCON_PASSWORD = os.getenv("RCON_PASSWORD")
# GEMINI_KEY = os.getenv("GEMINI_KEY")


# API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

# def send_api_request(prompt: str) -> str:
#     """Отправляет запрос к API Gemini с заданным промптом."""
#     from_prompt = "I gave you rp story that user write in our form for minecraft rp server, named DiceRP(Дайс), you must response true or false (nothic else, just word true or false), true when story is acceptable and false if not. Acceptable story mean character in story must be imagine, more acceptable story that tells how character describe characteristics of self, also acceptable some joke story. Not acceptable just stupid, bad spelling, story about real player, not enough describe person, Story looks like created in 5 second, flat not interest 'Meta-references' or 'authorial asides' are not allowed. work with this: " + prompt
#     headers = {
#         "Content-Type": "application/json",
#     }
#     data = {
#         "contents": [
#             {
#                 "parts": [{"text": prompt}]
#             }
#         ]
#     }

#     try:
#         response = requests.post(API_URL, headers=headers, json=data)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Ошибка при отправке запроса: {e}")
#         return None


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