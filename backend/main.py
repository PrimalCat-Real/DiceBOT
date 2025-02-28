from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class ConnectionRequest(BaseModel):
    username: str
    ip: str

@app.post("/v1/allowConnectByApi")
async def allow_connection(request: ConnectionRequest):
    ip_address = request.ip
    sudo_password = os.getenv("SUDO_PASSWORD")

    if not sudo_password:
        return {"error": "Sudo password not set in .env file."}

    try:
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

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)