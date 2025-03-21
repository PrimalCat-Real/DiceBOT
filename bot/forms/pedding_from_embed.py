from difflib import SequenceMatcher
from discord import Embed
import discord
# from bot.buttons.accept_form_button import AcceptFormButton


from config import FORM_STATUSES


class PenddingFormEmbedManager:
    MODERATOR_ROLE_ID = 1294635010053242941
    
    @staticmethod
    async def send_decision_embed(client, form_data, user_data, db_manager):
        # guild_id = 993224057464041552
        # decision_channel_id = db_manager.get_decision_channel_id(guild_id)
        guild_id = db_manager.get_first_guild_id()
        if not guild_id:
            raise ValueError("Guild ID не найден в базе данных.")

        # Получаем ID канала для решений
        decision_channel_id = db_manager.get_decision_channel_id(guild_id)
        if not decision_channel_id:
            raise ValueError("Канал для решений не настроен.")

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

                from bot.buttons.accept_form_button import AcceptFormButton
                accept_button = AcceptFormButton(db_manager, form_data)
                from bot.buttons.decline_form_button import DeclineFormButton
                decline_button = DeclineFormButton(db_manager, form_data)
                from bot.embed_manager import EmbedManager
                view = EmbedManager.create_view([accept_button, decline_button])
                button_types = ['AcceptFormButton', 'DeclineFormButton']
                message = await EmbedManager.send_embed_with_view(decision_channel, embed, view, button_types, db_manager)
                return message.id
                
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
        

from aiogram import Bot
from aiogram.types import Message
from database.database import DatabaseManager
from config import FORM_STATUSES

class TelegramFormStatusEmbedManager:
    @staticmethod
    async def send_status_message(bot: Bot, db_manager: DatabaseManager, user_id: int, mc_username: str):
        form = db_manager.forms.find_one({"mc_username": mc_username, "telegram_user_id": user_id})
        if not form:
            return

        status_key = form["status"]
        status = FORM_STATUSES.get(status_key, FORM_STATUSES["pending"])
        message_text = TelegramFormStatusEmbedManager.create_status_message(status, form)

        try:
            await bot.send_message(chat_id=form["telegram_chat_id"], text=message_text, parse_mode="Markdown")
            print(f"Статус анкеты для пользователя {user_id} отправлен: {status.name}")
        except Exception as e:
            print(f"Произошла ошибка при отправке статуса анкеты пользователю {user_id}: {e}")

    @staticmethod
    def create_status_message(status, form):
        if status.key == "pending":
            return f"Статус вашей анкеты: {status.name}\nВаша анкета находится на рассмотрении."
        elif status.key == "approved":
            return f"Статус вашей анкеты: {status.name}\nДобро пожаловать на сервер! Приятной игры!\n" \
                f"[Лаунчер](https://drive.google.com/file/d/15G-zZevRi3co09n1YERWwd0wvA1vRYOx/view?usp=sharing)\n" \
                f"[Сборка Модов](https://drive.google.com/file/d/1kFx-rqNIDHSH3iUqgszaCq5n4xXSilfj/view?usp=sharing)"
        elif status.key == "rejected":
            reason = form.get("reason", "Причина не указана")
            return f"Статус вашей анкеты: {status.name}\nВаша анкета была отклонена.\nПричина: {reason}"
        elif status.key == "deleted":
            return f"Статус вашей анкеты: {status.name}\nВаша анкета была удалена."
        else:
            return "Статус вашей анкеты: Неизвестно\nСтатус вашей анкеты не определен."
    
    