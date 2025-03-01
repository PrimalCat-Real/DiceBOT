from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime

from bot.forms.pedding_from_embed import TelegramFormStatusEmbedManager
from database.database import DatabaseManager
from bot.embed_manager import PenddingFormEmbedManager
from config import FORM_FIELDS

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

        if self.db_manager.check_form_duplicate(mc_username):
            await message.answer("Анкета с таким ником уже существует.")
            return
    
        self.db_manager.forms.update_one({"mc_username": mc_username}, {"$set": form_data})

        # self.db_manager.forms.insert_one(form_data)
        await TelegramFormStatusEmbedManager.send_status_message(self.bot, self.db_manager, user_id, mc_username) # Отправляем уведомление

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

from aiogram.fsm.state import StatesGroup, State

class FormState(StatesGroup):
    waiting_for_answer = State()