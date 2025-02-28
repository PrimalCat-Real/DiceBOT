import discord
from discord import Interaction, ButtonStyle

class FillFormButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=ButtonStyle.primary, label="Заполнить анкету")

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message("Кнопка 'Заполнить анкету' нажата!", ephemeral=True)