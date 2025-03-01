
import discord
from discord import Interaction, ButtonStyle

from bot.forms.discord_form import DiscordForm
from config import FORM_FIELDS
from database.database import DatabaseManager
from config import messages
class FillFormButton(discord.ui.Button):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(style=ButtonStyle.primary, label="Заполнить анкету")
        self.db_manager = db_manager

    async def callback(self, interaction: Interaction):
        user_id = interaction.user.id
        discord_name = interaction.user.name
        existing_form = self.db_manager.forms.find_one({
            "discord_user_id": user_id,
            "status": {"$in": ["pending", "approved"]} 
        })

        if existing_form:
            await interaction.response.send_message(messages["existing_form_error"], ephemeral=True)
            return

        form = DiscordForm("Анкета", FORM_FIELDS, self.db_manager) 
        await form.create_modal(interaction)