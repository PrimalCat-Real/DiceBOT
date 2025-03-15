import discord
from discord import Button, ButtonStyle, app_commands, Interaction
from discord import Interaction, ui
import logging

from bot.buttons.buy_product_button import BuyProductButton
from bot.buttons.check_tokens_button import CheckTokensButton
from bot.buttons.fill_form_button import FillFormButton
from bot.buttons.token_purchase_button import TokenPurchaseButton
from bot.embed_manager import EmbedManager
from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
from config import messages, is_admin
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
            app_commands.Choice(name="send_donate_message", value="send_donate_message"),
        ])
        async def discord_command(interaction: Interaction, command: app_commands.Choice[str]):
            if not is_admin(interaction):
                await interaction.response.send_message("У вас недостаточно прав для выполнения этой команды.", ephemeral=True)
                return
            commands = {
                "set_guild_id": self.set_guild_id,
                "send_welcome_message": self.send_welcome_message,
                "set_decision_channel": self.set_decision_channel,
                "set_approved_channel": self.set_approved_channel,
                "set_purchase_channel": self.set_purchase_channel,
                "send_donate_message": self.send_donate_message,
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
        embed.set_image(url="https://media.discordapp.net/attachments/1204083354698252329/1297945998269747223/Group_10.png")
        button = FillFormButton(self.db_manager)

        discord_link_button = ui.Button(style=ButtonStyle.link, url="https://drive.google.com/file/d/15G-zZevRi3co09n1YERWwd0wvA1vRYOx/view?usp=sharing", label="Скачать Лаунчер")
        how_to_fill_form_button = ui.Button(style=ButtonStyle.link, url="https://discord.com/channels/1294073178116849694/1347217887726932018", label="Как заполнить анкету?")

        view = EmbedManager.create_view([button, discord_link_button, how_to_fill_form_button])
        button_types = ['FillFormButton', 'discord.ui.Button.link', 'discord.ui.Button.link']
        message = await EmbedManager.send_embed_with_view(interaction.channel, embed, view, button_types, self.db_manager)

    async def set_purchase_channel(self, interaction: Interaction):
        channel_id = interaction.channel.id
        guild_id = interaction.guild.id
        self.db_manager.set_purchase_channel_id(guild_id, channel_id)
        await interaction.response.send_message(f"ID канала для уведомлений о покупках ({interaction.channel.name} - {channel_id}) успешно сохранён.", ephemeral=True)
        self.logger.info(f"Purchase channel ID {channel_id} has been saved.")
        
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

    async def send_donate_message(self, interaction: Interaction):
        embed = messages["donate_embed"]
        # easydonate_button = ui.Button(style=ButtonStyle.link, url="YOUR_EASYDONATE_LINK", label="Поддержать через EasyDonate")
        check_tokens_button = CheckTokensButton(self.db_manager)
        token_purchase_button = TokenPurchaseButton()
        buy_product_button = BuyProductButton(self.db_manager)
        view = EmbedManager.create_view([check_tokens_button, token_purchase_button, buy_product_button])
        button_types = ['CheckTokensButton', 'TokenPurchaseButton', 'BuyProductButton']
        await EmbedManager.send_embed_with_view(interaction.channel, embed, view, button_types, self.db_manager)
        await interaction.response.send_message("Сообщение с донатом отправлено!", ephemeral=True)

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