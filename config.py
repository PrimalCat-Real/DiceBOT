from discord import Color, Embed
import discord

from bot.forms.form import FormField, FormStatus

PLAYER_ROLE_ID = 1294631037212688548
RULES_CHANNEL_ID = 1294627794571100200
GUIDES_CHANNEL_ID = 1294631463983120455



admin_roles = [1301580747634638859, 1301580770607104070, 1301580815314063360, 1301580795466743838]
moder_roles = [1294635010053242941, 1330811514558484492]

guild_id = 993224057464041552

def is_admin(interaction: discord.Interaction) -> bool:
    """
    Проверяет, является ли пользователь администратором.
    :param interaction: Объект Interaction из discord.py.
    :return: True, если пользователь администратор, иначе False.
    """
    if isinstance(interaction.user, discord.Member):
        user_roles = interaction.user.roles
        return any(role.id in admin_roles for role in user_roles)
    else:
        return False

def is_moderator(interaction: discord.Interaction) -> bool:
    """
    Проверяет, является ли пользователь модератором.
    :param interaction: Объект Interaction из discord.py.
    :return: True, если пользователь модератор, иначе False.
    """
    if isinstance(interaction.user, discord.Member):
        user_roles = interaction.user.roles
        return any(role.id in moder_roles or role.id in admin_roles for role in user_roles)
    else:
        return False


FORM_FIELDS = [
    FormField("Ник в игре", "Minecraft ник, который будет добавлен в вайт-лист", key="minecraft_username", required=True, max_length=24, regex=r"^[a-zA-Z0-9_]{3,16}$"),
    FormField("Реальный Возраст", "Ваш возраст", key="real_age", max_length=2, regex=r"^\d{2,}$", required=True),
    FormField("Опыт RP", "Нет | Минимальный | Средний | Высокий", key="rp_experience", max_length=256, required=True),
    FormField("История персонажа RP", "История ИГРОВОГО(ВЫДУМАННОГО) персонажа, за которого вы будете отыгрывать РП", key="rp_character_story", min_length=150, required=True, max_length=1024, field_type="textarea"),
    FormField("Как вы узнали о сервере?", "Расскажите, где вы узнали о нашем сервере или от кого", key="how_did_you_find_us", max_length=1024, required=False)
]

FORM_STATUSES = {
    "pending": FormStatus("pending", "В ожидании", 0xFFCA3A),
    "approved": FormStatus("approved", "Одобрено", 0x2ECF03),
    "rejected": FormStatus("rejected", "Отклонено", 0xFF595E),
    "deleted": FormStatus("deleted", "Удалено", 0x808080),
}

messages = {
    "donate_embed": Embed(
        title="🎲 DiceRolePlay | Товары сервера",
        description=(
            "Если вы желаете поддержать наш сервер материально 💰 и взамен получить эксклюзивные предметы и возможности ✨, "
            "раздел доната идеально подходит для этих целей. Здесь представлены уникальные товары 🛒, которые не только "
            "улучшат ваш игровой опыт 🎮, но и помогут выделиться среди других игроков. 🏆\n\n"
            "🔍 **Как это работает?**\n\n"
            "1️⃣ Выберите товар из выпадающего списка ниже, где рядом с названием указана его цена. 🛍️\n"
            "2️⃣ При наличии нужного количества токенов 🪙, у вас появится сообщение с кнопкой покупки, которую вы можете нажать. 💳\n"
            "3️⃣ Администрации приходит запрос о вашей покупке 📩, по которому они свяжутся с вами для выдачи товара. 🤝\n\n"
            "‎🎉 Поддержка сервера через донат позволяет нам развивать и улучшать игровой мир, предлагая вам и другим игрокам новые "
            "возможности и интересные обновления. 🚀 Ваш вклад помогает нам создавать более качественный и увлекательный игровой процесс. ❤️"
        ),
        color=0x9535C9
    ),
    "welcome_embed": Embed(
            title="Регистрация на сервере Dice | RP 🎲",
            description=(
                 f" **Зачем нужна анкета?**\n"
                f"Анкета необходима для получения роли <@&{PLAYER_ROLE_ID}>, а также для доступа к серверу и возможности взаимодействовать с другими игроками и Администрацией.\n\n"
                f"1️⃣**Что нужно сделать перед заполнением анкеты?**\n"
                f"Перед заполнением анкеты ОБЯЗАТЕЛЬНО прочти (<#{RULES_CHANNEL_ID}>) нашего сервера.\n\n"
                f"2️⃣ **Как правильно отвечать на вопросы анкеты?**\n"
                f"🔑 Отвечай честно и по существу. В вопросах, где нужно описать персонажа, постарайся предоставить как можно больше деталей — это увеличит шансы на получение роли! Прочитать руководство по заполнению анкеты вы можете в канале: (<#{GUIDES_CHANNEL_ID}>)😎\n\n"
                f"Удачи в регистрации! 🎉"
            ),
            color=0x9535C9
        ),
    "existing_form_error": "У вас уже есть анкета",
    "existing_form_nick_error": "Анкета с таким ником уже существует"
}

PRODUCTS = [
    {"name": "Кастомная пластинка 1шт. – 200 руб", "cost": 200, "description": "Эксклюзивная кастомная пластинка для вашего использования."},
    {"name": "Кастомная пластинка 3шт. – 450 руб", "cost": 450, "description": "Три уникальные кастомные пластинки с выгодой."},
    {"name": "Откат инвентаря – 450 руб", "cost": 450, "description": "Восстановление вашего инвентаря после потери."},
    {"name": "Разбан – 1000 руб", "cost": 1000, "description": "Снятие блокировки с вашего аккаунта."},
    {"name": "Кастомная голова 1шт. – 65 руб", "cost": 65, "description": "Создание уникальной кастомной головы."},
    {"name": "Кастомная голова 3шт. – 185 руб", "cost": 185, "description": "Три кастомные головы по сниженной цене."},
    {"name": "Картинка на карте 1шт. –  35 руб", "cost": 35, "description": "Добавление изображения на одну карту."},
    {"name": "Картинка на карте 10шт. – 350 руб", "cost": 350, "description": "Десять изображений на карте с выгодой."},
    {"name": "Кастомный лор и имя предмета – 150 руб", "cost": 150, "description": "Уникальное описание и имя для предмета."},
    {"name": "Смена аккаунта – 80 руб", "cost": 80, "description": "1 покупка — 1 смена аккаунта."},
    {"name": "Смена роста 300 руб", "cost": 300, "description": "Доступные размеры: 0.7, 1 и 1.3."},
    {"name": "Снятие мута – 149 руб", "cost": 149, "description": "Снятие мута с вашего аккаунта."},
    {"name": "Выпустить из тюрьмы – 179 руб", "cost": 179, "description": "Освобождение из тюрьмы."},
]