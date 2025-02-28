from datetime import datetime
import discord

from bot.forms.form import Form
from bot.messages.ds_from_msg_sending import FormStatusEmbedManager
from config import FORM_FIELDS, PLAYER_ROLE_ID, is_admin, is_moderator
from database.database import DatabaseManager
from config import messages

class DiscordForm(Form):
    def __init__(self, title, fields, db_manager: DatabaseManager):
        super().__init__(title, fields)
        self.db_manager = db_manager

    async def create_modal(self, interaction: discord.Interaction):
        class FormModal(discord.ui.Modal, title=self.title):
            def __init__(self, form: DiscordForm, new_db_manager: DatabaseManager):
                super().__init__()
                self.form = form
                self.db_manager = new_db_manager
                for field in form.fields:
                    if field.field_type == "text":
                        self.add_item(discord.ui.TextInput(label=field.name, placeholder=field.placeholder, style=discord.TextStyle.short, required=field.required, min_length=field.min_length, max_length=field.max_length))
                    elif field.field_type == "textarea":
                        self.add_item(discord.ui.TextInput(label=field.name, placeholder=field.placeholder, style=discord.TextStyle.paragraph, required=field.required, min_length=field.min_length, max_length=field.max_length))



            async def on_submit(self, interaction: discord.Interaction):
                for i, field in enumerate(FORM_FIELDS):
                    self.form.data[field.key] = self.children[i].value

                user_id = interaction.user.id
                mc_username = self.form.data.get("minecraft_username", None)
                age = self.form.data.get("real_age", None)
                rp_story = self.form.data.get("rp_character_story", None)

                errors = {}
                for field in FORM_FIELDS:
                    error = field.validate(self.form.data.get(field.key, ""))
                    if error:
                        errors[field.key] = error

                if errors:
                    error_message = "\n".join(errors.values())
                    await interaction.response.send_message(f"Ошибка валидации:\n{error_message}", ephemeral=True)
                    return


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

                existing_user = self.db_manager.users.find_one({"mc_username": mc_username})
                if existing_user:
                    update_data = {k: v for k, v in user_data.items() if k not in existing_user}
                    if update_data:
                        self.db_manager.users.update_one({"mc_username": mc_username}, {"$set": update_data})
                else:
                    self.db_manager.users.insert_one(user_data)

        
                if self.db_manager.check_form_duplicate(mc_username):
                    await interaction.response.send_message(messages["existing_form_nick_error"], ephemeral=True)
                    return

                self.db_manager.forms.insert_one(form_data)


                await interaction.response.send_message("Форма отправлена!", ephemeral=True)
                await FormStatusEmbedManager.send_status_embed(self.client, self.db_manager, self.logger, user_id, mc_username)

        await interaction.response.send_modal(FormModal(self, self.db_manager))