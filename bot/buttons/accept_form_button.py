import discord
from datetime import datetime
from config import FORM_STATUSES
from database.database import DatabaseManager

class AcceptFormButton(discord.ui.Button):
    def __init__(self, db_manager: DatabaseManager, form_data, *args, **kwargs):
        super().__init__(style=discord.ButtonStyle.success, label="Одобрить", *args, **kwargs)
        self.db_manager = db_manager
        self.form_data = form_data

    async def callback(self, interaction: discord.Interaction):
        class ReasonModal(discord.ui.Modal, title="Обновление статуса"):
            reason = discord.ui.TextInput(label="Причина", placeholder="Введите причину (необязательно)", required=False)

            async def on_submit(self, interaction: discord.Interaction):
                reason = self.reason.value if self.reason.value else "Не указано"
                await self.process_approval(interaction, reason)
                
            async def process_approval(self, interaction, reason):
                        self.db_manager.forms.update_one({"mc_username": self.form_data["mc_username"]}, {"$set": {"status": "approved", "approved_by": interaction.user.id, "approved_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "reason": reason}})
                        embed = interaction.message.embeds[0]
                        embed.set_field_at(embed.fields.index(next(field for field in embed.fields if field.name == "Статус")), name="Статус", value=FORM_STATUSES["approved"].name)
                        embed.add_field(name="Одобрено", value=f"<@{interaction.user.id}>", inline=False)
                        embed.add_field(name="Время одобрения", value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                        embed.add_field(name="Причина", value=reason, inline=False)

                        embed.color = discord.Color(FORM_STATUSES["approved"].color)

                        await interaction.response.edit_message(embed=embed, view=None)
                        self.db_manager.discord_messages.delete_one({"message_id": interaction.message.id})
                        # self.db_manager.forms.update_one({"mc_username": self.form_data["mc_username"]}, {"$set": {"status": "approved", "approved_by": interaction.user.id, "approved_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}})

                        # embed = interaction.message.embeds[0]
                        # embed.set_field_at(embed.fields.index(next(field for field in embed.fields if field.name == "Статус")), name="Статус", value=FORM_STATUSES["approved"].name)
                        # embed.add_field(name="Одобрено", value=f"<@{interaction.user.id}>", inline=False)
                        # embed.add_field(name="Время одобрения", value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)

                # await interaction.response.edit_message(embed=embed, view=None)
        await interaction.response.send_modal(ReasonModal())

      