# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import subprocess
# import os
# from dotenv import load_dotenv

# from database.database import DatabaseManager
# from logs import logging_config

# load_dotenv()

# app = FastAPI()

# connection_string = os.getenv("MONGODB")

# logger = logging_config.setup_logging()

# database_name = 'dice_bot_db'
# db_manager = DatabaseManager(connection_string, database_name)

# class ConnectionRequest(BaseModel):
#     username: str
#     ip: str

# def remove_existing_ip(ip_address: str, sudo_password: str):
#     try:
#         process_delete = subprocess.Popen(
#             ["sudo", "-S", "ufw", "delete", "allow", "from", ip_address, "to", "any", "port", "25565"],
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )
#         stdout, stderr = process_delete.communicate(input=sudo_password + "\n")
#         if process_delete.returncode != 0:
#             raise Exception(f"Failed to delete existing rule: {stderr}")
#     except Exception as e:
#         raise Exception(f"Error removing existing IP: {str(e)}")

# @app.post("/v1/allowConnectByApi")
# async def allow_connection(request: ConnectionRequest):
#     ip_address = request.ip
#     mc_username = request.username
#     sudo_password = os.getenv("SUDO_PASSWORD")

#     if not sudo_password:
#         raise HTTPException(status_code=500, detail="Sudo password not set in .env file.")

#     try:
#         print(f"Received connection request for {mc_username} from {ip_address}")
#         print(f"Searching for user {mc_username} in database...")
#         user = db_manager.users.find_one({"mc_username": mc_username})
#         print(f"Search result: {user}")

#         if not user:
#             print(f"User {mc_username} not found.")
#             raise HTTPException(status_code=404, detail="User not found.")

#         if "last_ip" in user and user["last_ip"]:
#             print(f"User {mc_username} has existing last_ip: {user['last_ip']}")
#             try:
#                 remove_existing_ip(user["last_ip"], sudo_password)
#                 print(f"Existing IP {user['last_ip']} removed for user {mc_username}.")
#             except Exception as e:
#                 print(f"Error removing existing IP for user {mc_username}: {str(e)}")
#                 raise HTTPException(status_code=500, detail=f"Error removing existing IP: {str(e)}")

#         print(f"Updating last_ip to {ip_address} for user {mc_username}.")
#         update_result = db_manager.users.update_one({"_id": user["_id"]}, {"$set": {"last_ip": ip_address}})
#         print(f"Update result: {update_result.modified_count} documents modified.")

#         print(f"Allowing connection from {ip_address} to port 25565.")
#         process_allow = subprocess.Popen(
#             ["sudo", "-S", "ufw", "allow", "from", ip_address, "to", "any", "port", "25565"],
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )
#         stdout, stderr = process_allow.communicate(input=sudo_password + "\n")
#         if process_allow.returncode != 0:
#             print(f"Failed to allow connection for {ip_address}: {stderr}")
#             raise HTTPException(status_code=500, detail=f"Failed to allow connection: {stderr}")

#         print(f"Connection allowed from {ip_address} to port 25565 for user {mc_username}.")
#         return {"message": f"Connection allowed from {ip_address} to port 25565"}

#     except HTTPException as http_exc:
#         raise http_exc
#     except Exception as e:
#         print(f"An unexpected error occurred for user {mc_username}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
import logging
import uvicorn
from fastapi import FastAPI

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)  # Установите нужный уровень логирования
logger.addHandler(logging.StreamHandler()) # Добавляем вывод в консоль

@app.get("/")
def read_root():
    logger.info("test ok")
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=800, log_level="info", debug=True)