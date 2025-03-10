import asyncio
from datetime import datetime, timedelta
import random
# from datetime import datetime, timedelta
import discord
from discord.ext import commands
# import requests

from bot.discord_commands import CommandManager
from bot.embed_manager import EmbedManager



from config import PLAYER_ROLE_ID
from database.database import DatabaseManager
import logging








class DiscordBot(commands.Bot):
    def __init__(self, token, command_prefix="!", intents=discord.Intents.default(), logger=logging, database_manager: DatabaseManager = None, tg_bot = None):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.token = token
        self.logger = logger
        self.database_manager = database_manager
        
        self.embed_manager = EmbedManager()
        self.client = self
        self.tg_bot = tg_bot
        self.discord_commands = CommandManager(self, database_manager, logger)

    def set_tg_bot(self, tg_bot):
        print("test tg bot", tg_bot)
        self.tg_bot = tg_bot

    async def on_ready(self):
        await self.tree.sync()
        self.logger.info("Discord bot is ready!")
        self.logger.info('------')
        await self.embed_manager.restore_all_embeds(self, self.database_manager, self.logger)
        asyncio.create_task(self.check_pending_forms(self.database_manager))

    async def run_bot(self):
        await self.start(self.token)

    async def check_pending_forms(self, db_manager: DatabaseManager):
        while True:
            
            pending_forms = db_manager.forms.find({"status": "pending"})
            for form in pending_forms:
                submission_time = datetime.strptime(form["submission_time"], "%Y-%m-%d %H:%M:%S")
                if datetime.now() - submission_time > timedelta(minutes=10):
                    rp_story = form["rp_story"]
                    from utils import send_api_request
                    gemini_response = send_api_request(rp_story)
                    if gemini_response is not None:  # Проверка на None перед обработкой
                        if gemini_response:  # True = approved
                            db_manager.forms.update_one({"mc_username": form["mc_username"]}, {"$set": {"status": "approved"}})
                            logging.info(f"Form {form['mc_username']} automatically approved by AI.")
                            # discord_id = int(form["discord_user_id"])
                            await self.update_embed_status(form, "approved")
                            # from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
                            # await FormStatusEmbedManager.send_status_embed(client, db_manager, discord_id, form["mc_username"])

                        else:  # False = rejected
                            db_manager.forms.update_one({"mc_username": form["mc_username"]}, {"$set": {"status": "rejected"}})
                            logging.info(f"Form {form['mc_username']} automatically rejected by AI.")
                            # discord_id = int(form["discord_user_id"])
                            await self.update_embed_status(form, "rejected")
                            db_manager.delete_form(form["mc_username"])
                            # from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
                            # await FormStatusEmbedManager.send_status_embed(client, db_manager, discord_id, form["mc_username"])
                    else:
                        logging.error(f"Gemini response was None for {form['mc_username']}.")
                        continue

            await asyncio.sleep(700)

    async def update_embed_status(self, form, status):
        from config import FORM_STATUSES
        form_data = self.database_manager.forms.find_one({"mc_username": form["mc_username"]})
        if form_data and form_data.get("message_id"):
            try:
                guild_id = self.database_manager.get_first_guild_id()
                if not guild_id:
                    guild_id = self.database_manager.get_first_guild_id()
                    if not guild_id:
                        logging.error("Guild ID not found in forms or configs.")
                        return
                channel_id = self.database_manager.get_decision_channel_id(guild_id)
                if not channel_id:
                    logging.error(f"Decision channel ID not found for guild {guild_id}")
                    return
                channel = self.client.get_channel(channel_id)
                message = await channel.fetch_message(form_data["message_id"])
                embed = message.embeds[0]

                embed.set_field_at(embed.fields.index(next(field for field in embed.fields if field.name == "Статус")), name="Статус", value=FORM_STATUSES[status].name)

                if status == "approved":
                    embed.add_field(name="Одобрено", value="AI", inline=False)
                    embed.add_field(name="Время одобрения", value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                    embed.add_field(name="Причина", value="Автоматическое одобрение Искусственным Интеллектом", inline=False)
                    self.database_manager.forms.update_one(
                        {"mc_username": form["mc_username"]},
                        {"$set": {"reason": "Автоматическое одобрение Искусственным Интеллектом", "approved_by": "AI"}}
                    )
                else:
                    embed.add_field(name="Отклонено", value="AI", inline=False)
                    embed.add_field(name="Время отклонения", value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                    embed.add_field(name="Причина", value="Автоматический отказ Искусственным Интеллектом", inline=False)
                    self.database_manager.forms.update_one(
                        {"mc_username": form["mc_username"]},
                        {"$set": {"reason": "Автоматический отказ Искусственным Интеллектом", "approved_by": "AI"}}
                    )

                # Обновление цвета
                embed.color = discord.Color(FORM_STATUSES[status].color)

                await message.edit(embed=embed, view=None)
                if status == "approved":
                    from utils import add_to_whitelist
                    if await add_to_whitelist(form["mc_username"]):
                        logging.info(f"{form['mc_username']} added to whitelist.")
                    await self.send_approved_embed(guild_id, form_data) 
                if form.get("discord_user_id"):
                    if status == "approved":
                         guild = self.client.get_guild(guild_id)
                    if not guild:
                        logging.error(f"Гильдия {guild_id} не найдена")
                        return
                    
                    role = guild.get_role(PLAYER_ROLE_ID)
                    if not role:
                        logging.error(f"Роль {PLAYER_ROLE_ID} не найдена")
                        return
                    
                    user_id = int(form["discord_user_id"])  # Убедись, что user_id - это число
                    user = guild.get_member(user_id)
                    if not user:
                        logging.error(f"Пользователь {user_id} не найден в гильдии")
                        return
                    
                    
                    await user.add_roles(role)
                    logging.info(f"Добавлена роль {role.name} пользователю {user.name}")

                self.database_manager.discord_embeds.delete_one({"message_id": form_data["message_id"]})
            
                if form.get("discord_user_id"):
                    from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
                    await FormStatusEmbedManager.send_status_embed(self.client, self.database_manager, int(form["discord_user_id"]), form["mc_username"])
                elif form.get("telegram_user_id"):
                    from bot.forms.pedding_from_embed import TelegramFormStatusEmbedManager
                    await TelegramFormStatusEmbedManager.send_status_message(self.client.tg_bot.bot, self.database_manager, int(form["telegram_user_id"]), form["mc_username"])
                
            except (discord.NotFound, discord.HTTPException) as e:
                logging.error(f"Failed to update embed for {form['mc_username']}: {e}")

    async def send_approved_embed(self, guild_id, form_data):
        channel_id = self.database_manager.get_approved_channel_id(guild_id)
        if channel_id:
            channel = self.client.get_channel(channel_id)
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
                    
    def close(self):
        loop = asyncio.get_running_loop()
        try:
            loop.create_task(asyncio.wait_for(self.close(), timeout=10))
        except RuntimeError:
            self.logger.warning("Event loop not running.")
        except Exception as e:
            self.logger.exception(f"Error closing bot: {e}")

