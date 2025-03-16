import logging
import random
import discord
from datetime import datetime


from config import FORM_STATUSES, PLAYER_ROLE_ID
from database.database import DatabaseManager


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
            async def add_role_by_nickname(self, interaction: discord.Interaction, nickname: str, role: discord.Role):
                members = interaction.guild.members
                found_members = [member for member in members if member.name == nickname]

                if len(found_members) == 1:
                    member = found_members[0]
                    try:
                        await member.add_roles(role)
                        print(f"Роль {role.name} добавлена пользователю {member.name}.", ephemeral=True)
                    except discord.Forbidden:
                        print("У бота нет прав для добавления ролей.", ephemeral=True)
                    except discord.HTTPException as e:
                        print(f"Ошибка при добавлении роли: {e}", ephemeral=True)
                elif len(found_members) > 1:
                    print("Найдено несколько пользователей с таким никнеймом. Пожалуйста, уточните поиск.", ephemeral=True)
                else:
                    print("Пользователь с таким никнеймом не найден.", ephemeral=True)
            async def process_approval(self, interaction, reason):
                self.db_manager.forms.update_one({"mc_username": self.form_data["mc_username"]}, {"$set": {"status": "approved", "approved_by": interaction.user.name, "approved_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "reason": reason}})
                embed = interaction.message.embeds[0]
                embed.set_field_at(embed.fields.index(next(field for field in embed.fields if field.name == "Статус")), name="Статус", value=FORM_STATUSES["approved"].name)
                embed.add_field(name="Одобрено", value=f"<@{interaction.user.id}>", inline=False)
                embed.add_field(name="Время одобрения", value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                embed.add_field(name="Причина", value=reason, inline=False)

                embed.color = discord.Color(FORM_STATUSES["approved"].color)
                
                
                from utils import add_to_whitelist
                if await add_to_whitelist(self.form_data["mc_username"]):
                    logging.info(f"{self.form_data['mc_username']} added to whitelist.")

                user_id = self.form_data.get("discord_user_id") or self.form_data.get("telegram_user_id")
                if user_id and self.form_data.get("discord_user_id"):
                    # user = interaction.guild.get_member()
                   
                    # user = interaction.guild.get_member(self.form_data.get("discord_user_id"))
                    # print(user)
                    role = interaction.guild.get_role(PLAYER_ROLE_ID)
                    if role:
                        
                       await self.add_role_by_nickname(interaction, role, self.form_data.get("discord_name"))
                       
                    # if user:
                    #     role = interaction.guild.get_role(PLAYER_ROLE_ID)
                    #     logging.info(f"{interaction.guild.id}")
                    #     if role and role not in user.roles:
                    #         try:
                    #             await user.add_roles(role)
                    #             logging.info(f"Role {role.name} added to {user.name}.")
                    #         except discord.Forbidden:
                    #             logging.error(f"Bot does not have permission to add role {role.name}.")
                    #         except discord.HTTPException as e:
                    #             logging.error(f"Failed to add role {role.name} to {user.name}: {e}")
                    else:
                        logging.warning(f"User with ID {self.form_data.get("discord_user_id")} not found in guild.")
                # guild = self.client.get_guild(guild_id)  # Получаем объект гильдии
                # if guild:
                #     try:
                #         user = await guild.fetch_member(user_id) #пытаемся получить юзера с гильдии
                #         if user:
                #             role = guild.get_role(PLAYER_ROLE_ID)
                #             if role and role not in user.roles:
                #                 try:
                #                     await user.add_roles(role)
                #                     logging.info(f"Role {role.name} added to {user.name} in guild {guild_id}.") # Добавлено guild_id
                #                 except discord.Forbidden:
                #                     logging.error(f"Bot does not have permission to add role {role.name} in guild {guild_id}.") # Добавлено guild_id
                #                 except discord.HTTPException as e:
                #                     logging.error(f"Failed to add role {role.name} to {user.name} in guild {guild_id}: {e}.") # Добавлено guild_id
                #         else:
                #             logging.warning(f"User with ID {user_id} not found in guild {guild_id}.") # Добавлено guild_id
                #     except discord.NotFound:
                #         logging.warning(f"User with ID {user_id} not found in guild {guild_id}.") # Добавлено guild_id

                await interaction.response.edit_message(embed=embed, view=None)
                self.db_manager.discord_embeds.delete_one({"message_id": interaction.message.id})
                
                if self.form_data.get("discord_user_id"):
                    from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
                    await FormStatusEmbedManager.send_status_embed(interaction.client, self.db_manager, user_id, self.form_data["mc_username"])
                elif self.form_data.get("telegram_user_id"):
                    # Получаем экземпляр бота из interaction.client
                    from bot.forms.pedding_from_embed import TelegramFormStatusEmbedManager
                    await TelegramFormStatusEmbedManager.send_status_message(interaction.client.tg_bot.bot, self.db_manager, int(user_id), self.form_data["mc_username"])
                # await FormStatusEmbedManager.send_status_embed(interaction.client, self.db_manager, user_id, self.form_data["mc_username"])
                await self.update_user_status_change(interaction, interaction.user.id, self.form_data["mc_username"])
                await self.send_approved_embed(interaction.client, interaction.guild.id, self.form_data)

            async def update_user_status_change(self, interaction, user_id, mc_username):
                user = self.db_manager.users.find_one({"discord_id": user_id})
                if user:
                    status_change_count = user.get("status_change_count", 0) + 1
                    forms_done = user.get("forms_done", [])
                    forms_done.append({
                        "mc_nickname": mc_username,
                        "status": "accept",
                        "approve_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    self.db_manager.users.update_one(
                        {"discord_id": user_id},
                        {"$set": {
                            "status_change_count": status_change_count,
                            "forms_done": forms_done,
                            "discord_name": interaction.user.name
                        }}
                    )
                else:
                    new_user = {
                        "discord_id": user_id,
                        "discord_name": interaction.user.name,
                        "status_change_count": 1,
                        "forms_done": [{
                            "mc_nickname": mc_username,
                            "status": "accept",
                            "approve_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }]
                    }
                    self.db_manager.users.insert_one(new_user)  
                    
            async def send_approved_embed(self, client, guild_id, form_data):
                channel_id = self.db_manager.get_approved_channel_id(guild_id)
                if channel_id:
                    channel = client.get_channel(channel_id)
                    if channel:
                        embed = discord.Embed(
                            title="Анкета принята:",
                            description=form_data["rp_story"],
                            color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                        )
                        embed.set_author(name=form_data.get("discord_name") or form_data.get("telegram_name"),
                                         icon_url=form_data.get("discord_avatar") or "https://cdn.pixabay.com/photo/2021/12/27/10/50/telegram-6896827_1280.png")
                        await channel.send(embed=embed)
                    else:
                        logging.error(f"Channel with ID {channel_id} not found.")
                else:
                    logging.error(f"Approved channel ID not set for guild {guild_id}.")

        await interaction.response.send_modal(ReasonModal(self.db_manager, self.form_data))