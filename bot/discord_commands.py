import discord
from discord import Button, ButtonStyle, app_commands, Interaction
import logging

from bot.buttons.fill_form_button import FillFormButton
from bot.embed_manager import EmbedManager
from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
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
            app_commands.Choice(name="set_decision_channel", value="set_decision_channel"),
            app_commands.Choice(name="set_approved_channel", value="set_approved_channel"),
            app_commands.Choice(name="delete_form", value="delete_form"),
        ])
        async def discord_command(interaction: Interaction, command: app_commands.Choice[str]):
            commands = {
                "set_guild_id": self.set_guild_id,
                "send_welcome_message": self.send_welcome_message,
                "set_decision_channel": self.set_decision_channel,
                "set_approved_channel": self.set_approved_channel,
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
        button = FillFormButton(self.db_manager)

        discord_link_button = Button(style=ButtonStyle.link, url="https://drive.google.com/file/d/15G-zZevRi3co09n1YERWwd0wvA1vRYOx/view?usp=sharing", label="Скачать Лаунчер")
        view = EmbedManager.create_view([button, discord_link_button])
        button_types = ['FillFormButton', 'discord.ui.Button']
        message = await EmbedManager.send_embed_with_view(interaction.channel, embed, view, button_types, self.db_manager)
    
    async def set_decision_channel(self, interaction: Interaction):
        channel_id = interaction.channel.id
        guild_id = interaction.guild.id
        self.db_manager.set_decision_channel_id(guild_id, channel_id)
        await interaction.response.send_message(f"ID канала для решений ({interaction.channel.name} - {channel_id}) успешно сохранён.", ephemeral=True)
        self.logger.info(f"Decision channel ID {channel_id} has been saved.")

    async def set_approved_channel(self, interaction: Interaction):
        channel_id = interaction.channel.id
        guild_id = interaction.guild.id
        self.db_manager.set_approved_channel_id(guild_id, channel_id)
        await interaction.response.send_message(f"ID канала для одобрения ({interaction.channel.name} - {channel_id}) успешно сохранён.", ephemeral=True)
        self.logger.info(f"Approved channel ID {channel_id} has been saved.")

    async def delete_form(self, interaction: Interaction):
        class DeleteFormModal(discord.ui.Modal, title="Удаление анкеты"):
            mc_username = discord.ui.TextInput(label="Ник Minecraft", placeholder="Введите ник Minecraft", required=True)

            async def on_submit(self, interaction: Interaction):
                mc_username = self.mc_username.value
                result = self.db_manager.delete_form(mc_username)
                if result.deleted_count > 0:
                    await interaction.response.send_message(f"Анкета пользователя {mc_username} успешно удалена.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Анкета пользователя {mc_username} не найдена.", ephemeral=True)

        await interaction.response.send_modal(DeleteFormModal(self))