import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from database.database import DatabaseManager

class TelegramBot:
    def __init__(self, token, logger=None, database_manager: DatabaseManager = None):
        self.token = token
        self.logger = logger
        self.database_manager = database_manager
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()

    async def start(self, message: types.Message):
        pass

    def register_handlers(self):
        self.dp.message.register(self.start, Command(commands=["start"]))

    async def run_bot(self):
        self.register_handlers()
        self.logger.info("Telegram bot is running!")
        try:
            await self.dp.start_polling(self.bot)
        finally:
            await self.bot.session.close()