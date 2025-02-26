import discord
from discord.ext import commands

from bot.discord_commands import CommandManager
from database.database import DatabaseManager
import logging

class DiscordBot(commands.Bot):
    def __init__(self, token, command_prefix="!", intents=discord.Intents.default(), logger=logging, database_manager: DatabaseManager = None):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.token = token
        self.logger = logger
        self.database_manager = database_manager
        self.discord_commands = CommandManager(self, database_manager, logger)

    async def on_ready(self):
        await self.tree.sync()
        self.logger.info("Discord bot is ready!")

    async def run_bot(self):
        await self.start(self.token)