
import logging
from discord import Interaction
from mcrcon import MCRcon

from main import RCON_HOST, RCON_PASSWORD, RCON_PORT

async def add_to_whitelist(mc_username: str) -> bool:
    try:
        rcon_port = int(RCON_PORT)
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=rcon_port) as mcr:
            command = f'whitelist add {mc_username}'
            mcr.command(command)
        logging.info(f"{mc_username} added to whitelist.")
        return True
    except Exception as e:
        logging.error(f"Failed to add {mc_username} to whitelist: {e}")
        return False