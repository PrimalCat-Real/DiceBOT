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
        # await self.embed_manager.restore_all_embeds(self, self.database_manager, self.logger)
        # messages = self.database_manager.get_discord_messages()
        # for message_data in messages:
        #     try:
        #         channel = self.get_channel(message_data['channel_id'])
        #         message = await channel.fetch_message(message_data['message_id'])

        #         embed = discord.Embed.from_dict(message_data['embed_data'])
        #         view = discord.ui.View()
        #         if message_data['view_data']:
        #             for button_data in message_data['view_data']:
        #                 button = discord.ui.Button.from_dict(button_data)
        #                 async def button_callback(interaction: discord.Interaction):
        #                     await interaction.response.send_message("Кнопка нажата!", ephemeral=True)
        #                 button.callback = button_callback
        #                 view.add_item(button)

        #         await EmbedManager.restore_view(message, view)
        #         self.logger.info(f"Restored embed and view for message {message.id} in channel {channel.id}.")
        #     except Exception as e:
        #         self.logger.error(f"Error restoring embed and view for message {message_data['message_id']}: {e}")

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