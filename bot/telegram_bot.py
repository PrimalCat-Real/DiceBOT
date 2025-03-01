import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from bot.forms.telegram_form import FormState, TelegramForm
from database.database import DatabaseManager
from aiogram.fsm.context import FSMContext

class TelegramBot:
    def __init__(self, token, logger=None, database_manager: DatabaseManager = None, discord_client = None):
        self.token = token
        self.logger = logger
        self.database_manager = database_manager
        self.bot = Bot(token=self.token)
        self.discord_client = discord_client 
        self.dp = Dispatcher()
        self.form = TelegramForm(self.bot, self.database_manager)

    async def start(self, message: types.Message, state: FSMContext):
        await self.form.start_form(message, state)

    async def process_answer(self, message: types.Message, state: FSMContext):
        await self.form.process_answer(message, state)

    def register_handlers(self):
        self.dp.message.register(self.start, Command(commands=["start"]))
        self.dp.message.register(self.process_answer, FormState.waiting_for_answer)

    async def run_bot(self):
        self.register_handlers()
        self.logger.info("Telegram bot is running!")
        try:
            await self.dp.start_polling(self.bot)
        finally:
            await self.bot.session.close()