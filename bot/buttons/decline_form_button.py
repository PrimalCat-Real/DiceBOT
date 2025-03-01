import logging
import discord
from datetime import datetime
from config import FORM_STATUSES
from database.database import DatabaseManager
from bot.messages.ds_from_msg_sending import FormStatusEmbedManager

class DeclineFormButton(discord.ui.Button):
    def __init__(self, db_manager: DatabaseManager, form_data, *args, **kwargs):
        super().__init__(style=discord.ButtonStyle.danger, label="Отклонить", *args, **kwargs)
        self.db_manager = db_manager
        self.form_data = form_data

    async def callback(self, interaction: discord.Interaction):
        class ReasonModal(discord.ui.Modal, title="Обновление статуса"):
            def __init__(self, db_manager, form_data):
                super().__init__()
                self.db_manager = db_manager
                self.form_data = form_data
            reason = discord.ui.TextInput(label="Причина", placeholder="Введите причину (необязательно)", required=False)

            async def on_submit(self, interaction: discord.Interaction):
                reason = self.reason.value if self.reason.value else "Не указано"
                await self.process_decline(interaction, reason)

            async def process_decline(self, interaction, reason):
                self.db_manager.forms.update_one({"mc_username": self.form_data["mc_username"]},
                                                 {"$set": {"status": "rejected", "rejected_by": interaction.user.id,
                                                           "rejected_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                           "reason": reason}})
                embed = interaction.message.embeds[0]
                embed.set_field_at(embed.fields.index(
                    next(field for field in embed.fields if field.name == "Статус")), name="Статус",
                                   value=FORM_STATUSES["rejected"].name)
                embed.add_field(name="Отклонено", value=f"<@{interaction.user.id}>", inline=False)
                embed.add_field(name="Время отклонения", value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                embed.add_field(name="Причина", value=reason, inline=False)

                embed.color = discord.Color(FORM_STATUSES["rejected"].color)

                await interaction.response.edit_message(embed=embed, view=None)
                self.db_manager.discord_embeds.delete_one({"message_id": interaction.message.id})
                user_id = self.form_data.get("discord_user_id") or self.form_data.get("telegram_user_id")
                # await FormStatusEmbedManager.send_status_embed(interaction.client, self.db_manager, user_id,
                #                                               self.form_data["mc_username"])
                await self.update_user_status_change(interaction.user.id, self.form_data["mc_username"])
                self.db_manager.delete_form(self.form_data["mc_username"])

            async def update_user_status_change(self, user_id, mc_username):
                user = self.db_manager.users.find_one({"discord_id": user_id})
                if user:
                    status_change_count = user.get("status_change_count", 0) + 1
                    forms_done = user.get("forms_done", [])
                    forms_done.append({"mc_nickname": mc_username, "status": "rejected", "approve_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                    self.db_manager.users.update_one({"discord_id": user_id}, {"$set": {"status_change_count": status_change_count, "forms_done": forms_done}})
                else:
                    new_user = {
                        "discord_id": user_id,
                        "status_change_count": 1,
                        "forms_done": [{"mc_nickname": mc_username, "status": "rejected", "approve_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
                    }
                    self.db_manager.users.insert_one(new_user)

        await interaction.response.send_modal(ReasonModal(self.db_manager, self.form_data))