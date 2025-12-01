from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any
from service import UserService
from utils import load_config, Logger

class UserConfig(BaseModel):
    discount_rate: float = Field(..., gt=0, lt=1)
    age_threshold: int = Field(40, ge=0, le=150)
    max_users: int = Field(100, gt=0)

class MainApp:
    def __init__(self):
        self._config = {}
        
    @property
    def config(self):
        return self._config
    
    def reload_config(self):
        try:
            new_config = load_config("settings.json")
            validated = UserConfig(**new_config).dict()
            self._config = validated
            return True
        except (ValidationError, Exception) as e:
            print(f"Config validation failed: {str(e)}")
            return False

app = FastAPI()
logger = Logger("app.log")
main_app = MainApp()

@app.on_event("startup")
async def startup_event():
    success = main_app.reload_config()
    if not success:
        raise RuntimeError("Failed to load initial configuration")

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
def create_user(payload: dict):
    try:
        validated_data = UserCreateRequest(**payload).dict()
        name = validated_data["name"]
        age = validated_data["age"]

        user = service.create_user(name=name, age=age)
        return {"created": user}
    except ValidationError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid request body: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error")

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

@app.get("/config")
def read_config():
    filtered_config = {
        k: v for k, v in main_app.config.items() 
        if k not in ["secret_key", "database_url"]
    }
    return filtered_config

@app.get("/health")
def health():
    return {"status": "ok"}