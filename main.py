python
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Optional, Dict, Any
from pydantic import BaseModel, ValidationError
from service import UserService
from utils import load_config, Logger
import json
from pathlib import Path
from datetime import datetime

class UserCreateModel(BaseModel):
    name: str
    age: int

class ConfigReloadResponse(BaseModel):
    success: bool
    message: str

app = FastAPI()
logger = Logger("app.log")

# Load config with fallback
try:
    config = load_config("settings.json", {
        "discount_rate": 0.1,
        "age_threshold": 40,
        "max_users": 1000
    })
except Exception as e:
    logger.error(f"Failed to load config: {e}")
    raise RuntimeError("Failed to load configuration") from e

# Initialize user storage with persistence
user_data_file = Path("users.json")
if user_data_file.exists():
    try:
        with open(user_data_file, "r") as f:
            users = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load user data: {e}")
        users = []
else:
    users = []

service = UserService(config=config, logger=logger)

def save_users():
    try:
        with open(user_data_file, "w") as f:
            json.dump(users, f)
    except Exception as e:
        logger.error(f"Failed to save user data: {e}")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

@app.get("/users")
def list_users():
    try:
        return {"users": service.list_users()}
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error")

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

@app.post("/users")
def create_user(payload: UserCreateModel):
    try:
        user = service.create_user(**payload.dict())
        users.append(user)
        save_users()
        return {"created": user}
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/discount/{user_id}")
def discount(user_id: int):
    try:
        value = service.calculate_discount(user_id)
        return {"discount": value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Discount error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

@app.get("/health")
def health():
    db_status = "ok" if user_data_file.exists() else "error"
    return {
        "status": "ok",
        "details": {
            "database": db_status,
            "config": "loaded" if config else "missing"
        }
    }

@app.get("/config/reload", response_model=ConfigReloadResponse)
def reload_config():
    global config
    try:
        config = load_config("settings.json", {
            "discount_rate": 0.1,
            "age_threshold": 40,
            "max_users": 1000
        })
        return {"success": True, "message": "Configuration reloaded successfully"}
    except Exception as e:
        logger.error(f"Failed to reload config: {e}")
        return {"success": False, "message": str(e)}