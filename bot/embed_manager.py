import discord
import json
from bot.buttons.fill_form_button import FillFormButton
from database.database import DatabaseManager  # Импортируйте ваши кастомные кнопки

class EmbedManager:

    BUTTON_TYPES = {
        'discord.ui.Button': discord.ui.Button,
        'FillFormButton': FillFormButton,
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
    async def send_embed_with_view(interaction, embed, button_types, db_manager: DatabaseManager):
        view = discord.ui.View()
        for button_type_name in button_types:
            button_class = EmbedManager.BUTTON_TYPES.get(button_type_name)
            if button_class:
                if button_type_name == 'discord.ui.Button':
                    button = button_class(style=discord.ButtonStyle.primary, label="Button")
                else:
                    button = button_class()
                view.add_item(button)

        message = await interaction.response.send_message(embed=embed, view=view)
        message = await interaction.original_response()

        embed_dict = embed.to_dict()
        db_manager.save_discord_message(message.id, message.channel.id, message.guild.id, embed_dict, button_types)

        return message

    @staticmethod
    async def send_embed(interaction, embed, db_manager: DatabaseManager):
        message = await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        # Сохранение эмбеда (без кнопок)
        embed_dict = embed.to_dict()
        db_manager.save_discord_message(message.id, message.channel.id, message.guild.id, embed_dict, None)

        return message

    # @staticmethod
    # async def send_embed_with_view(interaction, embed, view):
    #     await interaction.response.send_message(embed=embed, view=view)
    #     return await interaction.original_response()

    # @staticmethod
    # async def send_embed(interaction, embed):
    #     await interaction.response.send_message(embed=embed)
    #     return await interaction.original_response()


    # @staticmethod
    # def deserialize_view(button_data):
    #     if not button_data:
    #         return None
    #     view = discord.ui.View()
    #     for button_info in button_data:
    #         button_type_name = button_info['type']
    #         button_class = EmbedManager.BUTTON_TYPES.get(button_type_name)
    #         if button_class:
    #             if button_type_name == 'discord.ui.Button':
    #                 button = button_class(
    #                     style=discord.ButtonStyle(button_info['style']),
    #                     label=button_info.get('label'),
    #                     custom_id=button_info.get('custom_id'),
    #                     url=button_info.get('url'),
    #                     disabled=button_info.get('disabled', False),
    #                     emoji=button_info.get('emoji')
    #                 )
    #             else:
    #                 button = button_class()
    #             view.add_item(button)
    #     return view

    async def restore_all_embeds(self, bot, db_manager, logger):
        messages = db_manager.get_discord_messages()
        for message_data in messages:
            try:
                logger.info(message_data)
                channel = bot.get_channel(message_data['channel_id'])
                message = await channel.fetch_message(message_data['message_id'])

                embed = discord.Embed.from_dict(message_data['embed_data'])
                button_types = message_data.get('view_data', [])
                view = discord.ui.View()

                for button_type_name in button_types:
                    button_class = EmbedManager.BUTTON_TYPES.get(button_type_name)
                    if button_class:
                        if button_type_name == 'discord.ui.Button':
                            button = button_class(style=discord.ButtonStyle.primary, label="Button")
                        else:
                            button = button_class()
                        view.add_item(button)

                await message.edit(embed=embed, view=view)
                logger.info(f"Restored embed and view for message {message.id} in channel {channel.id}.")
            except Exception as e:
                logger.error(f"Error restoring embed and view for message {message_data['message_id']}: {e}")