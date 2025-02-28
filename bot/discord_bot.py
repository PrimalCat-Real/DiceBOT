import asyncio
import discord
from discord.ext import commands

from bot.discord_commands import CommandManager
from bot.embed_manager import EmbedManager
from database.database import DatabaseManager
import logging

class DiscordBot(commands.Bot):
    def __init__(self, token, command_prefix="!", intents=discord.Intents.default(), logger=logging, database_manager: DatabaseManager = None):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.token = token
        self.logger = logger
        self.database_manager = database_manager
        self.discord_commands = CommandManager(self, database_manager, logger)
        self.embed_manager = EmbedManager()

    async def on_ready(self):
        await self.tree.sync()
        self.logger.info("Discord bot is ready!")
        self.logger.info('------')
        await self.embed_manager.restore_all_embeds(self, self.database_manager, self.logger)

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