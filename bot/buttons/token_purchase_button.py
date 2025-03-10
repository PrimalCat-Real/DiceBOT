import discord
from discord import Interaction, ButtonStyle, ui
import requests
from config import SERVER_ID, PRODUCT_ID, SHOP_KEY

class TokenPurchaseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=ButtonStyle.green, label="Купить токены")

    async def callback(self, interaction: Interaction):
        # TODO ADD CHECK FOR APPROVED FORM
        modal = TokenPurchaseModal()
        await interaction.response.send_modal(modal)

class TokenPurchaseModal(ui.Modal, title="Покупка токенов"):
    def __init__(self):
        super().__init__()
        self.minecraft_nickname = ui.TextInput(label="Никнейм Minecraft", placeholder="Введите ваш никнейм в игре", required=True)
        self.amount = ui.TextInput(label="Количество токенов", placeholder="Введите количество, которое хотите купить", required=True)
        self.email = ui.TextInput(label="Email", placeholder="Введите ваш email", required=True)
        self.coupon = ui.TextInput(label="Купон (необязательно)", placeholder="Введите купон", required=False)

    async def on_submit(self, interaction: Interaction):
        nickname = self.minecraft_nickname.value
        amount = int(self.amount.value)
        email = self.email.value
        coupon = self.coupon.value

        server_id = SERVER_ID
        product_id = PRODUCT_ID
        shop_key = SHOP_KEY

        params = {
            "customer": nickname,
            "server_id": server_id,
            "products": f'{{"{product_id}": {amount}}}',
            "email": email,
            "success_url": "https://dicerp.easydonate.ru/"
        }
        if coupon:
            params["coupon"] = coupon

        headers = {"Shop-Key": shop_key}

        try:
            response = requests.get("https://easydonate.ru/api/v3/shop/payment/create", headers=headers, params=params)

            print("Статус ответа:", response.status_code)
            print("Ответ от API:", response.text)

            response_data = response.json()

            if response.status_code == 200 and response_data.get("success"):
                payment_url = response_data["response"]["url"]
                await interaction.response.send_message(f"Ссылка для оплаты: {payment_url}", ephemeral=True)
            else:
                await interaction.response.send_message("Ошибка при создании ссылки для оплаты. Попробуйте позже.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Произошла ошибка при обработке платежа.", ephemeral=True)
            print(f"Ошибка: {e}")