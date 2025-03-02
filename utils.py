
import logging
from discord import Interaction
from mcrcon import MCRcon
import requests

from main import RCON_HOST, RCON_PASSWORD, RCON_PORT, GEMINI_KEY
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
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
    



def send_api_request(prompt: str) -> str:
    from_prompt = "Я буду предоставлять вам ролевые истории, отправленные пользователями для Minecraft RP сервера DiceRP(Дайс). Ваша задача - отвечать 'true' или 'false'. Отвечайте 'true', если история приемлема, и 'false', если нет. Приемлемая история должна описывать вымышленного персонажа, содержать описание его характеристик, быть без грубых грамматических ошибок и не содержать неприемлемого контента. Желательно, чтобы история была детализированной, с логичным сюжетом и демонстрировала развитие персонажа, но это не обязательно. Небольшие 'мета-ссылки' допустимы, но чрезмерное их использование нежелательно. Неприемлемы истории о реальных игроках, с недостаточным описанием персонажа, созданные за короткое время или бессмысленные. Обращайте внимание на описание персонажа, так как истории с недостаточной детализацией менее предпочтительны. Вот история: " + prompt
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
