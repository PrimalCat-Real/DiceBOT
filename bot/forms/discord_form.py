import discord

from bot.forms.form import Form
from config import FORM_FIELDS

class DiscordForm(Form):
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