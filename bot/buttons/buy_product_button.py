
import discord
from discord import Embed, ui, ButtonStyle, Interaction

from bot.forms.discord_form import DiscordForm
from config import FORM_FIELDS
from database.database import DatabaseManager
from config import messages
from config import PRODUCTS
class BuyProductButton(discord.ui.Button):
    def __init__(self, db_manager):
        super().__init__(style=ButtonStyle.primary, label="Купить товар")
        self.db_manager = db_manager

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message("Выберите товар:", view=ProductSelectionView(self.db_manager), ephemeral=True)

class ProductSelect(ui.Select):
    def __init__(self, db_manager):
        self.db_manager = db_manager
        options = [
            discord.SelectOption(label=product["name"], description=product.get("description", "Нет описания"))
            for product in PRODUCTS
        ]
        super().__init__(placeholder="Выберите товар", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True) # defer the interaction
        selected_product_name = self.values[0]
        selected_product = next((product for product in PRODUCTS if product["name"] == selected_product_name), None)

        if selected_product:
            await interaction.followup.send( # use followup.send instead of response.send_message
                f"Вы выбрали {selected_product['name']} за {selected_product['cost']} токенов. Подтвердить покупку?",
                view=ConfirmPurchaseView(self.db_manager, selected_product, interaction.user.id),
                ephemeral=True
            )
        else:
            await interaction.followup.send("Товар не найден.", ephemeral=True)

class ProductSelectionView(ui.View):
    def __init__(self, db_manager):
        super().__init__()
        self.add_item(ProductSelect(db_manager))

class ConfirmPurchaseButton(ui.Button):
    def __init__(self, db_manager, product, user_id):
        super().__init__(style=ButtonStyle.success, label="Подтвердить покупку")
        self.db_manager = db_manager
        self.product = product
        self.user_id = user_id

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        user = self.db_manager.get_user_by_discord_id(self.user_id)
        if user and user.get("tokens", 0) >= self.product["cost"]:
            new_tokens = user["tokens"] - self.product["cost"]
            self.db_manager.update_user_tokens(self.user_id, new_tokens)
            await interaction.followup.send("Покупка успешно выполнена!", ephemeral=True)

            # Отправляем уведомление в канал
            purchase_channel_id = self.db_manager.get_purchase_channel_id(interaction.guild.id)
            if purchase_channel_id:
                purchase_channel = self.db_manager.client.get_channel(purchase_channel_id)
                if purchase_channel:
                    embed = Embed(
                        title="Новая покупка!",
                        description=f"Пользователь {interaction.user.mention} купил {self.product['name']} за {self.product['cost']} токенов.",
                        color=discord.Color.green()
                    )
                    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
                    await purchase_channel.send(embed=embed)
        else:
            await interaction.followup.send("Недостаточно токенов для покупки.", ephemeral=True)

class ConfirmPurchaseView(ui.View):
    def __init__(self, db_manager, product, user_id):
        super().__init__()
        self.add_item(ConfirmPurchaseButton(db_manager, product, user_id))