import discord
from discord import ButtonStyle, app_commands, Interaction
import logging

from bot.buttons.fill_form_button import FillFormButton
from bot.embed_manager import EmbedManager
from config import messages
from database.database import DatabaseManager
class CommandManager:
    def __init__(self, client, db_manager: DatabaseManager, logger=logging):
        self.client = client
        self.db_manager = db_manager
        self.logger = logger
        self.embed_manager = EmbedManager()
        self.setup_commands()

    def setup_commands(self):
        @self.client.tree.command(name="discord_command", description="Execute discord command from list [set_guild_id|send_welcome_message]")
        @app_commands.describe(command="Выберите команду для выполнения")
        @app_commands.choices(command=[
            app_commands.Choice(name="set_guild_id", value="set_guild_id"),
            app_commands.Choice(name="send_welcome_message", value="send_welcome_message"),
        ])
        async def discord_command(interaction: Interaction, command: app_commands.Choice[str]):
            commands = {
                "set_guild_id": self.set_guild_id,
                "send_welcome_message": self.send_welcome_message,
            }

            if command.value in commands:
                await commands[command.value](interaction)
            else:
                await interaction.response.send_message("Неизвестная команда.", ephemeral=True)

            # if not self.is_admin_or_moder(interaction):
            #     await interaction.response.send_message("У вас недостаточно прав для выполнения этой команды.", ephemeral=True)
            #     return
    async def set_guild_id(self, interaction: Interaction):
        guild_id = interaction.guild.id
        self.db_manager.set_guild_id(guild_id) 
        await interaction.response.send_message(f"ID гильдии {interaction.guild.name} ({guild_id}) успешно сохранён.", ephemeral=True)
        self.logger.info(f"Guild ID {guild_id} for guild {interaction.guild.name} has been saved.")

    async def send_welcome_message(self, interaction: Interaction):
        embed = messages["welcome_embed"]
        button = FillFormButton()

        view = EmbedManager.create_view([button])
        button_types = ['FillFormButton']
        message = await EmbedManager.send_embed_with_view(interaction.channel, embed, view, button_types, self.db_manager)