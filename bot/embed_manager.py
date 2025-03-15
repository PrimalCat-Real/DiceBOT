import discord
import json
from bot.buttons.accept_form_button import AcceptFormButton
from bot.buttons.check_tokens_button import CheckTokensButton
from bot.buttons.decline_form_button import DeclineFormButton
from bot.buttons.fill_form_button import FillFormButton
from bot.buttons.token_purchase_button import TokenPurchaseButton
from database.database import DatabaseManager
from discord import ui

class EmbedManager:

    BUTTON_TYPES = {
        'discord.ui.Button': discord.ui.Button,
        'FillFormButton': FillFormButton,
        'AcceptFormButton': AcceptFormButton,
        'DeclineFormButton': DeclineFormButton,
        'discord.ui.Button.link': discord.ui.Button,
        'CheckTokensButton': CheckTokensButton,
        'TokenPurchaseButton': TokenPurchaseButton
    }

    @staticmethod
    def create_embed(title, description, color=discord.Color.blue()):
        return discord.Embed(title=title, description=description, color=color)

    @staticmethod
    def create_view(buttons):
        view = discord.ui.View(timeout=None)
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
                view = discord.ui.View(timeout=None)
                used_link_buttons = []

                for button_type_name in button_types:
                    button_class = EmbedManager.BUTTON_TYPES.get(button_type_name)
                    if button_class:
                        if button_type_name == 'discord.ui.Button':
                            button = button_class(style=discord.ButtonStyle.primary, label="Button")
                        elif button_type_name == 'AcceptFormButton' or button_type_name == 'DeclineFormButton':
                            form_data = db_manager.get_form_data_by_message_id(message.id)
                            if form_data:
                                button = button_class(db_manager, form_data)
                            else:
                                logger.error(f"Form or user data not found for message {message.id}")
                                continue
                        elif button_type_name == 'CheckTokensButton':
                            button = button_class(db_manager)
                        elif button_type_name == 'TokenPurchaseButton':
                            button = button_class()
                        elif button_type_name == 'discord.ui.Button.link':
                            # Ищем неиспользованную кнопку-ссылку
                            link_button = next((item for item in message.components[0].children if item.url and item not in used_link_buttons), None)
                            if link_button:
                                button = button_class(url=link_button.url, label=link_button.label)
                                used_link_buttons.append(link_button) # Добавляем кнопку в список использованных
                            else:
                                logger.error(f"Link button with URL not found in message components for message {message.id}")
                                continue
                        else:
                            button = button_class(db_manager)
                        view.add_item(button)

                await message.edit(view=view)
                logger.info(f"Restored view for message {message.id} in channel {channel.id}.")
            except Exception as e:
                logger.error(f"Error restoring view for message {message_data['message_id']}: {e}")