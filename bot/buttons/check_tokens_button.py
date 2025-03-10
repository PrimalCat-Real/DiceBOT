import discord
from discord import Interaction, ButtonStyle
from database.database import DatabaseManager

class CheckTokensButton(discord.ui.Button):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(style=ButtonStyle.secondary, label="Проверить токены")
        self.db_manager = db_manager

    async def callback(self, interaction: Interaction):
        user_id = interaction.user.id
        user = self.db_manager.users.find_one({"discord_id": user_id})

        if user and "tokens" in user:
            tokens = user["tokens"]
            await interaction.response.send_message(f"У вас {tokens} токенов.", ephemeral=True)
        else:
            await interaction.response.send_message("У вас нет токенов.", ephemeral=True)