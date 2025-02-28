from discord import Color, Embed

from bot.forms.form import FormField, FormStatus

PLAYER_ROLE_ID = 1294631037212688548
RULES_CHANNEL_ID = 1294627794571100200

admin_roles = [1301580747634638859, 1301580770607104070, 1301580815314063360, 1301580795466743838]
moder_roles = [1294635010053242941, 1330811514558484492]

def is_admin(role_id):
    return role_id in admin_roles

def is_moderator(role_id):
    return role_id in moder_roles or role_id in admin_roles

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
    "welcome_embed": Embed(
            title="Регистрация на сервере Dice | RP 🎲",
            description=(
                 f"1️⃣ **Зачем нужна анкета?**\n"
                f"Анкета необходима для получения роли <@&{PLAYER_ROLE_ID}>, а также для доступа к серверу и возможности взаимодействовать с другими игроками и Администрацией.\n\n"
                f"2️⃣ **Что нужно сделать перед заполнением анкеты?**\n"
                f"Перед заполнением анкеты ОБЯЗАТЕЛЬНО прочти (<#{RULES_CHANNEL_ID}>) нашего сервера.\n\n"
                f"3️⃣ **Как правильно отвечать на вопросы анкеты?**\n"
                f"🔑 Отвечай честно и по существу. В вопросах, где нужно описать персонажа, постарайся предоставить как можно больше деталей — это увеличит шансы на получение роли! 😎\n\n"
                f"Удачи в регистрации! 🎉"
            ),
            color=0x9535C9
        ),
    "existing_form_error": "У вас уже есть анкета",
    "existing_form_nick_error": "Анкета с таким ником уже существует"
}