import discord
from discord import Interaction, ButtonStyle

from bot.forms.discord_form import DiscordForm
from config import FORM_FIELDS
from database.database import DatabaseManager

class FillFormButton(discord.ui.Button):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(style=ButtonStyle.primary, label="Заполнить анкету")
        self.db_manager = db_manager

    async def callback(self, interaction: Interaction):
        form = DiscordForm("Анкета", FORM_FIELDS, self.db_manager)
        await form.create_modal(interaction)