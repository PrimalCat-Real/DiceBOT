import discord
from discord import Interaction, ButtonStyle

from bot.forms.discord_form import DiscordForm
from config import FORM_FIELDS

class FillFormButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=ButtonStyle.primary, label="Заполнить анкету")

    async def callback(self, interaction: Interaction):
        form = DiscordForm("Форма", FORM_FIELDS)
        await form.create_modal(interaction)