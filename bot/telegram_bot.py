import asyncio
from aiogram import Bot, Dispatcher, types, html
from aiogram.filters import Command

from bot.forms.telegram_form import FormState, TelegramForm
from database.database import DatabaseManager
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

class TelegramBot:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self, token, logger=None, database_manager: DatabaseManager = None, discord_client = None):
        self.token = token
        self.logger = logger
        self.database_manager = database_manager
        self.bot = Bot(token=self.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.discord_client = discord_client 
        self.dp = Dispatcher()
        self.form = TelegramForm(self.bot, self.database_manager)
        discord_client.tg_bot = self

    async def start(self, message: types.Message, state: FSMContext):
        await self.form.start_form(message, state, self.discord_client)

    async def process_answer(self, message: types.Message, state: FSMContext):
        await self.form.process_answer(message, state)

    def register_handlers(self):
        self.dp.message.register(self.start, Command(commands=["start"]))
        self.dp.message.register(self.start, Command(commands=["fill_form"]))
        self.dp.message.register(self.send_info, Command(commands=["info"]))
        self.dp.message.register(self.process_answer, FormState.waiting_for_answer)

    async def send_info(self, message: types.Message):
        info_message = "Ссылки:\n" \
                       "[Лаунчер](https://drive.google.com/file/d/15G-zZevRi3co09n1YERWwd0wvA1vRYOx/view?usp=sharing)\n" \
                       "[Сборка Модов](https://drive.google.com/file/d/1kFx-rqNIDHSH3iUqgszaCq5n4xXSilfj/view?usp=sharing)\n" \
                       "[Discord канал](https://discord.gg/JEnpk5jAGq)\n" \
                       "[Обход блокировки](https://github.com/Filinsl/Discord-unlock)"
        await message.answer(info_message, parse_mode="Markdown")

    async def run_bot(self):
        self.register_handlers()
        self.logger.info("Telegram bot is running!")
        try:
            await self.dp.start_polling(self.bot)
        finally:
            await self.bot.session.close()