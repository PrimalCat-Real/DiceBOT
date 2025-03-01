import logging
import discord
from datetime import datetime
from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
from config import FORM_STATUSES, PLAYER_ROLE_ID
from database.database import DatabaseManager
from utils import add_to_whitelist

class AcceptFormButton(discord.ui.Button):
    def __init__(self, db_manager: DatabaseManager, form_data, *args, **kwargs):
        super().__init__(style=discord.ButtonStyle.success, label="Одобрить", *args, **kwargs)
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
                await self.process_approval(interaction, reason)

            async def process_approval(self, interaction, reason):
                self.db_manager.forms.update_one({"mc_username": self.form_data["mc_username"]}, {"$set": {"status": "approved", "approved_by": interaction.user.id, "approved_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "reason": reason}})
                embed = interaction.message.embeds[0]
                embed.set_field_at(embed.fields.index(next(field for field in embed.fields if field.name == "Статус")), name="Статус", value=FORM_STATUSES["approved"].name)
                embed.add_field(name="Одобрено", value=f"<@{interaction.user.id}>", inline=False)
                embed.add_field(name="Время одобрения", value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                embed.add_field(name="Причина", value=reason, inline=False)

                embed.color = discord.Color(FORM_STATUSES["approved"].color)
                
                

                if await add_to_whitelist(self.form_data["mc_username"]):
                    logging.info(f"{self.form_data['mc_username']} added to whitelist.")

                user = interaction.guild.get_member(self.user_data["discord_id"])
                if user:
                    role = interaction.guild.get_role(PLAYER_ROLE_ID)
                    if role and role not in user.roles:
                        try:
                            await user.add_roles(role)
                            logging.info(f"Role {role.name} added to {user.name}.")
                        except discord.Forbidden:
                            logging.error(f"Bot does not have permission to add role {role.name}.")
                        except discord.HTTPException as e:
                            logging.error(f"Failed to add role {role.name} to {user.name}: {e}")
                else:
                    logging.warning(f"User with ID {self.user_data['discord_id']} not found in guild.")
                await interaction.response.edit_message(embed=embed, view=None)
                self.db_manager.discord_embeds.delete_one({"message_id": interaction.message.id})
                await FormStatusEmbedManager.send_status_embed(interaction.client, self.db_manager, self.user_data["discord_id"], self.form_data["mc_username"])
                
        await interaction.response.send_modal(ReasonModal(self.db_manager, self.form_data))