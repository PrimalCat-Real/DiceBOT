import logging
import discord
from discord import Embed
from bot.forms.form import FormStatus
from config import FORM_STATUSES
from database.database import DatabaseManager

class FormStatusEmbedManager:
    @staticmethod
    async def send_status_embed(client, db_manager: DatabaseManager, user_id: int, mc_username: str):
        form = db_manager.forms.find_one({"mc_username": mc_username, "discord_user_id": user_id})
        if not form:
            return

        status_key = form["status"]
        status = FORM_STATUSES.get(status_key, FORM_STATUSES["pending"])
        embed = FormStatusEmbedManager.create_status_embed(status, form)

        try:
            user = await client.fetch_user(user_id)
            await user.send(embed=embed)
            print(f"Статус анкеты для пользователя {user_id} отправлен: {status.name}")
        # except discord.Forbidden:
        #     logger.error(f"Не удалось отправить личное сообщение пользователю {user_id}: Forbidden")
        # except discord.NotFound:
        #     logger.error(f"Пользователь {user_id} не найден")
        except Exception as e:
            print(f"Произошла ошибка при отправке статуса анкеты пользователю {user_id}: {e}")

    @staticmethod
    async def update_status_embed(client, db_manager: DatabaseManager, logger, user_id: int, mc_username: str):
        await FormStatusEmbedManager.send_status_embed(client, db_manager, logger, user_id, mc_username)

    @staticmethod
    def create_status_embed(status: FormStatus, form: dict) -> Embed:
        if status.key == "pending":
            return Embed(title=f"Статус вашей анкеты: {status.name}", description="Ваша анкета находится на рассмотрении.", color=status.color)
        elif status.key == "approved":
            embed = Embed(title=f"Статус вашей анкеты: {status.name}", description="Добро пожаловать на сервер! Приятной игры!", color=status.color)
            embed.add_field(name="IP сервера", value="play.dicerp.fun", inline=False)
            embed.add_field(name="Скачать лаунчер", value="[Скачать](https://drive.google.com/file/d/15G-zZevRi3co09n1YERWwd0wvA1vRYOx/view?usp=sharing)", inline=False)
            return embed
        elif status.key == "rejected":
            reason = form.get("reason", "Причина не указана")
            embed = Embed(title=f"Статус вашей анкеты: {status.name}", description="Ваша анкета была отклонена.", color=status.color)
            embed.add_field(name="Причина", value=reason, inline=False)
            embed.set_footer(text="Dice | RP")
            return embed
        elif status.key == "deleted":
            return Embed(title=f"Статус вашей анкеты: {status.name}", description="Ваша анкета была удалена.", color=status.color)
        else:
            return Embed(title="Статус вашей анкеты: Неизвестно", description="Статус вашей анкеты не определен.", color=FORM_STATUSES["pending"].color)