from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
from dotenv import load_dotenv
from pymongo import MongoClient  # Импортируем MongoClient для работы с MongoDB

load_dotenv()

app = FastAPI()

# Настройка подключения к MongoDB
MONGODB_URI = os.getenv("MONGODB")
DATABASE_NAME = "dice_bot_db"  # Замените на имя вашей базы данных
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
users_collection = db["users"]  # Предполагается, что коллекция называется "users"

class ConnectionRequest(BaseModel):
    username: str
    ip: str

@app.post("/v1/allowConnectByApi")
async def allow_connection(request: ConnectionRequest):
    ip_address = request.ip
    mc_username = request.username
    sudo_password = ""

    try:
        # Проверяем, существует ли пользователь с таким ником
        user = users_collection.find_one({"mc_username": mc_username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Добавляем IP-адрес в базу данных
        users_collection.update_one(
            {"mc_username": mc_username},
            {"$set": {"last_ip": ip_address}}
        )

        # Разрешаем соединение через ufw
        process_allow = subprocess.Popen(
            ["sudo", "-S", "ufw", "allow", "from", ip_address, "to", "any", "port", "25565"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process_allow.communicate(input=sudo_password + "\n")
        if process_allow.returncode != 0:
            return {"error": f"Failed to allow connection: {stderr}"}

        return {"message": f"Connection allowed from {ip_address} to port 25565"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)