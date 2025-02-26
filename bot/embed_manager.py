import discord

class EmbedManager:
    @staticmethod
    def create_embed(title, description, color=discord.Color.blue()):
        embed = discord.Embed(title=title, description=description, color=color)
        return embed

    @staticmethod
    def create_embed_with_buttons(title, description, buttons, color=discord.Color.blue()):
        embed = discord.Embed(title=title, description=description, color=color)
        view = discord.ui.View()
        for button in buttons:
            view.add_item(button)
        return embed, view

    @staticmethod
    async def restore_embed_with_buttons(message, buttons):
        view = discord.ui.View()
        for button in buttons:
            view.add_item(button)
        await message.edit(view=view)