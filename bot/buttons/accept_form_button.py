import discord
from datetime import datetime
from config import FORM_STATUSES
from bot.embed_manager import EmbedManager

class AcceptFormButton(discord.ui.Button):
    def __init__(self, db_manager, form_data, user_data, *args, **kwargs):
        super().__init__(style=discord.ButtonStyle.success, label="Одобрить", *args, **kwargs)
        self.db_manager = db_manager
        self.form_data = form_data
        self.user_data = user_data

    async def callback(self, interaction: discord.Interaction):
        self.db_manager.forms.update_one({"mc_username": self.form_data["mc_username"]}, {"$set": {"status": "approved", "approved_by": interaction.user.id, "approved_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}})

        embed = interaction.message.embeds[0]
        embed.set_field_at(embed.fields.index(next(field for field in embed.fields if field.name == "Статус")), name="Статус", value=FORM_STATUSES["approved"].name)
        embed.add_field(name="Одобрено", value=f"<@{interaction.user.id}>", inline=False)
        embed.add_field(name="Время одобрения", value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)

        await interaction.response.edit_message(embed=embed, view=None)