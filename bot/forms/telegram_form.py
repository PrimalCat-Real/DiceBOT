import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime

import discord

from bot.forms.pedding_from_embed import PenddingFormEmbedManager, TelegramFormStatusEmbedManager
from database.database import DatabaseManager
from config import FORM_FIELDS, FORM_STATUSES


class TelegramForm:
    def __init__(self, bot, db_manager: DatabaseManager):
        self.bot = bot
        self.db_manager = db_manager
        self.fields = FORM_FIELDS
        self.data = {}
        self.current_field_index = 0
    async def finish_form(self, message: types.Message, state: FSMContext):
        """Завершает заполнение формы и сохраняет данные."""
        await state.clear()

        user_id = message.from_user.id
        mc_username = self.data.get("minecraft_username", None)
        age = self.data.get("real_age", None)

        user_data = {
            "telegram_name": message.from_user.full_name,
            "telegram_id": user_id,
            "mc_username": mc_username,
            "age": age,
        }

        form_data = {
            "telegram_name": message.from_user.full_name,
            "telegram_user_id": user_id,
            "mc_username": mc_username,
            "age": age,
            "rp_experience": self.data.get("rp_experience", None),
            "rp_story": self.data.get("rp_character_story", None),
            "source_info": self.data.get("how_did_you_find_us", "Не указал"),
            "submission_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "pending",
            "telegram_chat_id": message.chat.id
        }

        existing_user = self.db_manager.users.find_one({"mc_username": mc_username})
        if existing_user:
            update_data = {k: v for k, v in user_data.items() if k not in existing_user}
            if update_data:
                self.db_manager.users.update_one({"mc_username": mc_username}, {"$set": update_data})
        else:
            self.db_manager.users.insert_one(user_data)

        # Проверка дубликата анкеты
        if self.db_manager.check_form_duplicate(mc_username):
            await message.answer("Анкета с таким ником уже существует.")
            return

        # Сохранение или обновление данных в forms
        existing_form = self.db_manager.forms.find_one({"mc_username": mc_username})
        if existing_form:
            self.db_manager.forms.update_one({"mc_username": mc_username}, {"$set": form_data})
        else:
            self.db_manager.forms.insert_one(form_data)

        await TelegramFormStatusEmbedManager.send_status_message(self.bot, self.db_manager, user_id, mc_username)
        await self.send_form_to_discord(form_data)

        await message.answer("Анкета отправлена!")

    async def start_form(self, message: types.Message, state: FSMContext):
        """Начинает процесс заполнения формы."""
        self.data = {}
        self.current_field_index = 0

        # Проверка уникальности ника
        mc_username = self.db_manager.forms.find_one({
            "mc_username": message.text,
            "status": {"$in": ["pending", "approved"]}
        })
        if mc_username:
            await message.answer("Ник уже используется в активной анкете.")
            return

        # Проверка уникальности Telegram ID
        telegram_id = self.db_manager.forms.find_one({
        "telegram_user_id": message.from_user.id,
        "status": {"$in": ["pending", "approved"]}
        })
        if telegram_id:
            await message.answer("Вы уже подали анкету.")
            return

        await state.set_state(FormState.waiting_for_answer)
        await message.answer(self.fields[self.current_field_index].name)

    async def process_answer(self, message: types.Message, state: FSMContext):
        """Обрабатывает ответ пользователя и переходит к следующему вопросу."""
        field = self.fields[self.current_field_index]
        self.data[field.key] = message.text

        error = field.validate(message.text)
        if error:
            await message.answer(f"Ошибка: {error}\n{field.name}")
            return

        self.current_field_index += 1
        if self.current_field_index < len(self.fields):
            await message.answer(self.fields[self.current_field_index].name)
        else:
            await self.finish_form(message, state)
    
    async def send_form_to_discord(self, form_data):
        logging.info("Starting send_form_to_discord...")
        guild_id = 993224057464041552  # Замените на ID вашего сервера
        decision_channel_id = self.db_manager.get_decision_channel_id(guild_id)
        if not guild_id:
            logging.warning("Guild ID not found in database.")
            return

        if not decision_channel_id:
            logging.warning(f"Decision channel ID not found for guild {guild_id}.")
            return
        
        try:
            from main import discord_bot_instance
            decision_channel = discord_bot_instance.get_channel(decision_channel_id)

            if not decision_channel:
                logging.warning(f"Decision channel with ID {decision_channel_id} not found.")
                return

            embed = discord.Embed(title="Анкета (Telegram)", color=0x2AABEE)
            embed.set_author(name=form_data['telegram_name'], icon_url="https://static.vecteezy.com/system/resources/previews/023/986/562/non_2x/telegram-logo-telegram-logo-transparent-telegram-icon-transparent-free-free-png.png")

            embed.add_field(name="Ник Minecraft", value=form_data['mc_username'], inline=False)
            embed.add_field(name="Возраст", value=form_data['age'], inline=False)
            embed.add_field(name="RP опыт", value=form_data['rp_experience'], inline=False)
            embed.add_field(name="RP история персонажа", value=form_data['rp_story'], inline=False)
            embed.add_field(name="Как вы нас нашли", value=form_data['source_info'], inline=False)
            embed.add_field(name="Время подачи", value=form_data['submission_time'], inline=False)

            similarity_message = PenddingFormEmbedManager.check_rp_story_similarity(form_data, self.db_manager)
            embed.add_field(name="Схожесть анкет", value=similarity_message, inline=False)

            form_status = FORM_STATUSES[form_data["status"]]
            embed.add_field(name="Статус", value=form_status.name, inline=False)

            await decision_channel.send(embed=embed)
            logging.info(f"Form sent to Discord channel {decision_channel_id}.")

        except Exception as e:
            logging.error(f"Error sending form to Discord: {e}", exc_info=True)

from aiogram.fsm.state import StatesGroup, State

class FormState(StatesGroup):
    waiting_for_answer = State()