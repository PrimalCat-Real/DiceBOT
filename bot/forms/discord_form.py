from datetime import datetime
import discord

from bot.forms.form import Form
from config import FORM_FIELDS, PLAYER_ROLE_ID, is_admin, is_moderator
from database.database import DatabaseManager

class DiscordForm(Form):
    def __init__(self, title, fields, db_manager: DatabaseManager):
        super().__init__(title, fields)
        self.db_manager = db_manager

    async def create_modal(self, interaction: discord.Interaction):
        class FormModal(discord.ui.Modal, title=self.title):
            def __init__(self, form: DiscordForm):
                super().__init__()
                self.form = form
                for field in form.fields:
                    if field.field_type == "text":
                        self.add_item(discord.ui.TextInput(label=field.name, placeholder=field.placeholder, style=discord.TextStyle.short, required=field.required))
                    elif field.field_type == "textarea":
                        self.add_item(discord.ui.TextInput(label=field.name, placeholder=field.placeholder, style=discord.TextStyle.paragraph, required=field.required))



            async def on_submit(self, interaction: discord.Interaction):
                for i, field in enumerate(FORM_FIELDS):
                    self.form.data[field.name] = self.children[i].value
                
                user_id = interaction.user.id
                mc_username = self.form.data["Ник в игре"]
                age = self.form.data.get("Реальный Возраст", None)


                user_roles = [role.id for role in interaction.user.roles]
                discord_role = None
                if any(is_admin(role_id) for role_id in user_roles):
                    discord_role = "admin"
                elif any(is_moderator(role_id) for role_id in user_roles):
                    discord_role = "moderator"
                
                # TODO add check if some field already exist
                # TODO check if user submit form from telegram, add in tg command for link discord
                # TODO on tg link send in welcome form

                

                user_data = {
                    "discord_name": interaction.user.name,
                    "discord_id": user_id,
                    "discord_created_at": interaction.user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "mc_username": mc_username,
                    "age": age,
                    "discord_role": discord_role
                }

                form_data = {
                    "discord_name": interaction.user.name,
                    "discord_avatar": interaction.user.avatar.url if interaction.user.avatar else "",
                    "discord_user_id": user_id,
                    "discord_created_at": interaction.user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "mc_username": mc_username,
                    "age": age,
                    "rp_experience": self.form.data.get("rp_experience", None),
                    "rp_story": self.form.data.get("rp_character_story", None),
                    "source_info": self.form.data.get("how_did_you_find_us", None),
                    "submission_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "В ожидании"
                }

                print(form_data)



                await interaction.response.send_message("Форма отправлена!", ephemeral=True)
                # # Проверка наличия пользователя
                # existing_form = forms_collection.find_one({"mc_username": self.form.data["Ник в игре"]})
                # if existing_form:
                #     await interaction.response.send_message(MESSAGES["user_exists"].format(mc_username=self.form.data["Ник в игре"]), ephemeral=True)
                #     return

                # # Сохранение данных в базу данных
                # user_info = {
                #     "Discord Username": interaction.user.name,
                #     "User ID": interaction.user.id,
                #     "Account Created At": interaction.user.created_at.strftime('%Y-%m-%d %H:%M:%S')
                # }
                # form_data = {
                #     "discord_username": interaction.user.name,
                #     "discord_avatar": interaction.user.avatar.url if interaction.user.avatar else "",
                #     "mc_username": self.form.data["Ник в игре"],
                #     "age": self.form.data["Реальный Возраст"],
                #     "rp_experience": self.form.data["Опыт RP"],
                #     "rp_story": self.form.data["История персонажа RP"],
                #     "source_info": self.form.data["Как вы узнали о сервере?"],
                #     "user_info": user_info,
                #     "submission_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                #     "status": "В ожидании"
                # }

                # forms_collection.update_one({"discord_username": interaction.user.name}, {"$set": form_data}, upsert=True)

                # await interaction.response.send_message(MESSAGES["form_submitted"], ephemeral=True)

        await interaction.response.send_modal(FormModal(self))