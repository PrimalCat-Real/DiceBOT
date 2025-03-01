from difflib import SequenceMatcher
from discord import Embed
import discord

from bot.embed_manager import EmbedManager
from config import FORM_STATUSES


class PenddingFormEmbedManager:
    MODERATOR_ROLE_ID = 1234567890
    
    @staticmethod
    async def send_decision_embed(client, form_data, user_data, db_manager):
        guild_id = 993224057464041552
        decision_channel_id = db_manager.get_decision_channel_id(guild_id)

        if decision_channel_id:
            decision_channel = client.get_channel(decision_channel_id)
            if decision_channel:
                embed = Embed(title="Анкета", color=0xFFFF00)
                embed.set_author(name=form_data['discord_name'], icon_url=form_data['discord_avatar'])

                embed.add_field(name="Ник Minecraft", value=form_data['mc_username'], inline=False)
                embed.add_field(name="Возраст", value=form_data['age'], inline=False)
                embed.add_field(name="RP опыт", value=form_data['rp_experience'], inline=False)
                embed.add_field(name="RP история персонажа", value=form_data['rp_story'], inline=False)
                embed.add_field(name="Как вы нас нашли", value=form_data['source_info'], inline=False)
                embed.add_field(name="Время подачи", value=form_data['submission_time'], inline=False)

                if user_data and 'discord_created_at' in user_data:
                    embed.add_field(name="Время создания Discord аккаунта", value=user_data['discord_created_at'], inline=False)
                else:
                    embed.add_field(name="Время создания Discord аккаунта", value=form_data['submission_time'], inline=False)

                # Проверка схожести анкет
                similarity_message = PenddingFormEmbedManager.check_rp_story_similarity(form_data, db_manager)
                embed.add_field(name="Схожесть анкет", value=similarity_message, inline=False)
                form_status = FORM_STATUSES[form_data["status"]]
                embed.add_field(name="Статус", value=form_status.name, inline=False)  # Используем form_status.name
                from bot.buttons.accept_form_button import AcceptFormButton #импортируем тут
                accept_button = AcceptFormButton(db_manager, form_data, user_data)
                view = discord.ui.View()
                view.add_item(accept_button)

                # Отправляем эмбед с кнопкой через EmbedManager
                button_types = ['AcceptFormButton']
                await EmbedManager.send_embed_with_view(decision_channel, embed, view, button_types, db_manager)
                # await decision_channel.send(content=f"<@&{PenddingFormEmbedManager.MODERATOR_ROLE_ID}>", embed=embed)

    @staticmethod
    def calculate_similarity(form1, form2):
        return SequenceMatcher(None, form1.get("rp_story", ""), form2.get("rp_story", "")).ratio() * 100

    @staticmethod
    def check_rp_story_similarity(form_data, db_manager):
        """Проверяет схожесть rp_story с одобренными анкетами."""
        approved_forms = db_manager.forms.find({"status": "Одобрено"})
        max_similarity = 0
        for approved_form in approved_forms:
            similarity = PenddingFormEmbedManager.calculate_similarity(form_data, approved_form)
            max_similarity = max(max_similarity, similarity)

        if max_similarity < 25:
            return "Оригинальная анкета"
        else:
            return f"Схожесть: {max_similarity:.2f}%"