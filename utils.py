
import logging
from discord import Interaction
from mcrcon import MCRcon
import requests

from main import RCON_HOST, RCON_PASSWORD, RCON_PORT, GEMINI_KEY

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
    

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

def send_api_request(prompt: str) -> str:
    from_prompt = "I gave you rp story that user write in our form for minecraft rp server, named DiceRP(Дайс), you must response true or false (nothic else, just word true or false), true when story is acceptable and false if not. Acceptable story mean character in story must be imagine, acceptable story that tells how character describe characteristics of self, also acceptable some joke story. Not acceptable just stupid, bad spelling, story about real player, not enough describe person, Story looks like created in 5 second, flat not interest 'Meta-references' or 'authorial asides' are not allowed, Pay attention to the character's description. Stories lacking in detail about the character's personality, background, or physical appearance should be less accaptable. work with this: " + prompt
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "contents": [
            {
                "parts": [{"text": from_prompt}]
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        # Извлекаем текст ответа из JSON
        response_text = response_json['candidates'][0]['content']['parts'][0]['text']
        if "true" in response_text:
            return True
        elif "false" in response_text:
            return False
        else:
            return False

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None

    
# response = send_api_request("Был на свете Бабаджи он был добрым всем помогал он жил в стране Ммайнкрафт а точнее городе Майнер. Работает шахтером и увлекается строительством и както раз он гулял по просторам твитча и наткнулся на стрим человека который играл на DiceRP он увидел что все игроки были добрыми и решил зайти туда. Конец")

# if response:
#     print(response)
