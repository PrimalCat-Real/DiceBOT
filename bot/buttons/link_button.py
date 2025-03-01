import discord

class LinkButton(discord.ui.Button):
    def __init__(self, url: str, label: str, *args, **kwargs):
        super().__init__(style=discord.ButtonStyle.link, url=url, label=label, *args, **kwargs)