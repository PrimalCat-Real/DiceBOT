import asyncio
# from datetime import datetime, timedelta
import discord
from discord.ext import commands
# import requests

from bot.discord_commands import CommandManager
from bot.embed_manager import EmbedManager
from database.database import DatabaseManager
import logging


# API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

# def send_api_request(prompt: str) -> str:
#     from_prompt = "I gave you rp story that user write in our form for minecraft rp server, named DiceRP(Дайс), you must response true or false (nothic else, just word true or false), true when story is acceptable and false if not. Acceptable story mean character in story must be imagine, more acceptable story that tells how character describe characteristics of self, also acceptable some joke story. Not acceptable just stupid, bad spelling, story about real player, not enough describe person, Story looks like created in 5 second, flat not interest 'Meta-references' or 'authorial asides' are not allowed. work with this: " + prompt
#     headers = {
#         "Content-Type": "application/json",
#     }
#     data = {
#         "contents": [
#             {
#                 "parts": [{"text": from_prompt}]
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

# async def check_pending_forms(db_manager: DatabaseManager, client):
#     while True:
#         try:
#             pending_forms = db_manager.forms.find({"status": "pending"})
#             for form in pending_forms:
#                 submission_time = datetime.strptime(form["submission_time"], "%Y-%m-%d %H:%M:%S")
#                 if datetime.now() - submission_time > timedelta(minutes=1):
#                     rp_story = form["rp_story"]
#                     gemini_response = send_api_request(rp_story)
#                     if gemini_response:
#                         try:
#                             content = gemini_response["candidates"][0]["content"]["parts"][0]["text"].lower()
#                             if "true" in content:
#                                 db_manager.forms.update_one({"mc_username": form["mc_username"]}, {"$set": {"status": "approved"}})
#                                 logging.info(f"Form {form['mc_username']} automatically approved by AI.")
#                                 discord_id = int(form["discord_user_id"])
#                                 from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
#                                 await FormStatusEmbedManager.send_status_embed(client, db_manager, discord_id, form["mc_username"])

#                             elif "false" in content:
#                                 db_manager.forms.update_one({"mc_username": form["mc_username"]}, {"$set": {"status": "rejected"}})
#                                 logging.info(f"Form {form['mc_username']} automatically rejected by AI.")
#                                 discord_id = int(form["discord_user_id"])
#                                 from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
#                                 await FormStatusEmbedManager.send_status_embed(client, db_manager, discord_id, form["mc_username"])
#                         except (KeyError, IndexError) as e:
#                             logging.error(f"Error parsing Gemini response for {form['mc_username']}: {e}")
#                             continue

#         except Exception as e:
#             logging.error(f"Error checking pending forms: {e}")

#         await asyncio.sleep(60)  # Проверяем каждые 10 минут



class DiscordBot(commands.Bot):
    def __init__(self, token, command_prefix="!", intents=discord.Intents.default(), logger=logging, database_manager: DatabaseManager = None):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.token = token
        self.logger = logger
        self.database_manager = database_manager
        
        self.embed_manager = EmbedManager()
        self.client = self
        self.tg_bot = None
        self.discord_commands = CommandManager(self, database_manager, logger)

    def set_tg_bot(self, tg_bot):
        self.tg_bot = tg_bot

    async def on_ready(self):
        await self.tree.sync()
        self.logger.info("Discord bot is ready!")
        self.logger.info('------')
        await self.embed_manager.restore_all_embeds(self, self.database_manager, self.logger)
        # asyncio.create_task(check_pending_forms(self.database_manage, self.client))

    async def run_bot(self):
        await self.start(self.token)

    def close(self):
        loop = asyncio.get_running_loop()
        try:
            loop.create_task(asyncio.wait_for(self.close(), timeout=10))
        except RuntimeError:
            self.logger.warning("Event loop not running.")
        except Exception as e:
            self.logger.exception(f"Error closing bot: {e}")

