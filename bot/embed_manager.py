import discord
import json
from bot.buttons.accept_form_button import AcceptFormButton
from bot.buttons.fill_form_button import FillFormButton
from database.database import DatabaseManager  # Импортируйте ваши кастомные кнопки

class EmbedManager:

    BUTTON_TYPES = {
        'discord.ui.Button': discord.ui.Button,
        'FillFormButton': FillFormButton,
        'AcceptFormButton': AcceptFormButton,
    }

    @staticmethod
    def create_embed(title, description, color=discord.Color.blue()):
        return discord.Embed(title=title, description=description, color=color)

    @staticmethod
    def create_view(buttons):
        view = discord.ui.View()
        for button in buttons:
            view.add_item(button)
        return view

    @staticmethod
    async def restore_view(message, view):
        await message.edit(view=view)

    @staticmethod
    async def send_embed_with_view(channel: discord.TextChannel, embed, view: discord.ui.View, button_types: list[str], db_manager: DatabaseManager):
        message = await channel.send(embed=embed, view=view)

        db_manager.save_discord_message(message.id, channel.id, message.guild.id, button_types)

        return message


    async def restore_all_embeds(self, bot, db_manager, logger):
        messages = db_manager.get_discord_messages()
        for message_data in messages:
            try:
                logger.info(message_data)
                channel = bot.get_channel(message_data['channel_id'])
                message = await channel.fetch_message(message_data['message_id'])

                button_types = message_data.get('button_types', [])
                view = discord.ui.View()

                for button_type_name in button_types:
                    button_class = EmbedManager.BUTTON_TYPES.get(button_type_name)
                    if button_class:
                        if button_type_name == 'discord.ui.Button':
                            button = button_class(style=discord.ButtonStyle.primary, label="Button")
                        else:
                            button = button_class(db_manager)
                        view.add_item(button)

                await message.edit(view=view)
                logger.info(f"Restored view for message {message.id} in channel {channel.id}.")
            except Exception as e:
                logger.error(f"Error restoring view for message {message_data['message_id']}: {e}")