from discord import Embed

from bot.forms.form import FormField

PLAYER_ROLE_ID = 1294631037212688548
RULES_CHANNEL_ID = 1294627794571100200

admin_roles = [1301580747634638859, 1301580770607104070, 1301580815314063360, 1301580795466743838]
moder_roles = [1294635010053242941, 1330811514558484492]

def is_admin(role_id):
    return role_id in admin_roles

def is_moderator(role_id):
    return role_id in moder_roles or role_id in admin_roles

FORM_FIELDS = [
    FormField("Ник в игре", "Minecraft ник, который будет добавлен в вайт-лист", max_length=24),
    FormField("Реальный Возраст", "Ваш возраст", max_length=2, regex=r"^\d+$", required=False),
    FormField("Опыт RP", "Нет | Минимальный | Средний | Высокий", max_length=256, required=False),
    FormField("История персонажа RP", "История ИГРОВОГО(ВЫДУМАННОГО) персонажа, за которого вы будете отыгрывать РП", min_length=150, max_length=1024, field_type="textarea"),
    FormField("Как вы узнали о сервере?", "Расскажите, где вы узнали о нашем сервере или от кого", max_length=1024, required=False)
]

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
        )
}