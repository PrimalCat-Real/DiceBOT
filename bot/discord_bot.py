import asyncio
from datetime import datetime, timedelta
# from datetime import datetime, timedelta
import discord
from discord.ext import commands
# import requests

from bot.discord_commands import CommandManager
from bot.embed_manager import EmbedManager
from database.database import DatabaseManager
import logging

from utils import send_api_request






class DiscordBot(commands.Bot):
    def __init__(self, token, command_prefix="!", intents=discord.Intents.default(), logger=logging, database_manager: DatabaseManager = None, tg_bot = None):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.token = token
        self.logger = logger
        self.database_manager = database_manager
        
        self.embed_manager = EmbedManager()
        self.client = self
        self.tg_bot = tg_bot
        self.discord_commands = CommandManager(self, database_manager, logger)

    def set_tg_bot(self, tg_bot):
        print("test tg bot", tg_bot)
        self.tg_bot = tg_bot

    async def on_ready(self):
        await self.tree.sync()
        self.logger.info("Discord bot is ready!")
        self.logger.info('------')
        await self.embed_manager.restore_all_embeds(self, self.database_manager, self.logger)
        asyncio.create_task(self.check_pending_forms(self.database_manage, self.client))

    async def run_bot(self):
        await self.start(self.token)

    async def check_pending_forms(self, db_manager: DatabaseManager):
        while True:
            try:
                pending_forms = db_manager.forms.find({"status": "pending"})
                for form in pending_forms:
                    submission_time = datetime.strptime(form["submission_time"], "%Y-%m-%d %H:%M:%S")
                    if datetime.now() - submission_time > timedelta(minutes=1):
                        rp_story = form["rp_story"]
                        gemini_response = send_api_request(rp_story)
                        if gemini_response is not None:  # Проверка на None перед обработкой
                            if gemini_response:  # True = approved
                                # db_manager.forms.update_one({"mc_username": form["mc_username"]}, {"$set": {"status": "approved"}})
                                logging.info(f"Form {form['mc_username']} automatically approved by AI.")
                                discord_id = int(form["discord_user_id"])
                                # from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
                                # await FormStatusEmbedManager.send_status_embed(client, db_manager, discord_id, form["mc_username"])

                            else:  # False = rejected
                                # db_manager.forms.update_one({"mc_username": form["mc_username"]}, {"$set": {"status": "rejected"}})
                                logging.info(f"Form {form['mc_username']} automatically rejected by AI.")
                                discord_id = int(form["discord_user_id"])
                                # from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
                                # await FormStatusEmbedManager.send_status_embed(client, db_manager, discord_id, form["mc_username"])
                        else:
                            logging.error(f"Gemini response was None for {form['mc_username']}.")
                            continue

            except Exception as e:
                logging.error(f"Error checking pending forms: {e}")

            await asyncio.sleep(60)  # Проверяем каждые 10 минут

    def close(self):
        loop = asyncio.get_running_loop()
        try:
            loop.create_task(asyncio.wait_for(self.close(), timeout=10))
        except RuntimeError:
            self.logger.warning("Event loop not running.")
        except Exception as e:
            self.logger.exception(f"Error closing bot: {e}")

