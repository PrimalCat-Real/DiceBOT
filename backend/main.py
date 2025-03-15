import logging
import logging.handlers
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import subprocess
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

app = FastAPI()

# Настройка логирования
log_file = "app.log"
log_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logging.basicConfig(level=logging.INFO, handlers=[log_handler])

# Настройка подключения к MongoDB
MONGODB_URI = os.getenv("MONGODB")
DATABASE_NAME = "dice_bot_db"
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
users_collection = db["users"]

class ConnectionRequest(BaseModel):
    username: str
    ip: str

@app.post("/api/payment/easydonate/handler")
async def handle_payment(request: Request):
    data = await request.json()
    logging.info(f"Получен callback с данными: {data}")

    customer = data.get("customer")
    products = data.get("products", [])
    tokens_count = sum(product.get("count", 0) for product in products)

    user = users_collection.find_one({"mc_username": customer})

    if user:
        if "tokens" in user:
            new_tokens_count = user["tokens"] + tokens_count
        else:
            new_tokens_count = tokens_count

        users_collection.update_one(
            {"mc_username": customer},
            {"$set": {"tokens": new_tokens_count}}
        )
        logging.info(f"Обновлено количество токенов для {customer}: {new_tokens_count}")
    else:
        users_collection.insert_one({
            "mc_username": customer,
            "tokens": tokens_count
        })
        logging.info(f"Создана запись для {customer} с {tokens_count} токенами")

    return {"status": "success"}

@app.post("/v1/allowConnectByApi")
async def allow_connection(request: ConnectionRequest):
    ip_address = request.ip
    mc_username = request.username
    sudo_password = ""

    try:
        user = users_collection.find_one({"mc_username": mc_username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        users_collection.update_one(
            {"mc_username": mc_username},
            {"$set": {"last_ip": ip_address}}
        )

        process_allow = subprocess.Popen(
            ["sudo", "-S", "ufw", "allow", "from", ip_address, "to", "any", "port", "25565"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process_allow.communicate(input=sudo_password + "\n")
        if process_allow.returncode != 0:
            logging.error(f"Failed to allow connection: {stderr}")
            return {"error": f"Failed to allow connection: {stderr}"}

        logging.info(f"Connection allowed from {ip_address} to port 25565")
        return {"message": f"Connection allowed from {ip_address} to port 25565"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return {"error": f"An unexpected error occurred: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)