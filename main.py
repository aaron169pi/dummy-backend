from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any
from service import UserService
from utils import load_config, Logger

class ConfigModel(BaseModel):
    discount_rate: float = Field(..., gt=0, lt=1)
    age_threshold: int = Field(40, ge=0, le=150)
    db_connection: str
    secret_key: str
    
class ConfigResponse(BaseModel):
    discount_rate: float
    age_threshold: int

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)

app = FastAPI()
logger = Logger("app.log")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config with fallback
try:
    config = load_config("settings.json")
except Exception as e:
    logger.error(f"Failed to load config: {str(e)}. Using default values.")
    config = {
        "discount_rate": 0.1,
        "age_threshold": 40,
        "db_connection": "sqlite:///:memory:",
        "secret_key": "dev-secret-key"
    }

# Validate config
try:
    ConfigModel(**config).dict()
except ValidationError as e:
    logger.error(f"Config validation failed: {str(e)}")
    raise

service = UserService(config=config, logger=logger)


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
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


@app.post("/users")
def create_user(payload: CreateUserRequest = Body(...)):
    try:
        user = service.create_user(name=payload.name, age=payload.age)
        return {"created": user}
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/discount/{user_id}")
def discount(user_id: int):
    try:
        value = service.calculate_discount(user_id)
        return {"discount": value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Discount calculation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/config", response_model=ConfigResponse)
def read_config():
    """Return non-sensitive config values"""
    filtered_config = {
        "discount_rate": config["discount_rate"],
        "age_threshold": config["age_threshold"]
    }
    return filtered_config


@app.post("/config/reload")
def reload_config():
    """Reload configuration from file"""
    try:
        global config
        new_config = load_config("settings.json")
        ConfigModel(**new_config).dict()  # Validate before replacing
        config = new_config
        return {"success": True, "message": "Config reloaded successfully"}
    except Exception as e:
        logger.error(f"Config reload failed: {str(e)}")
        return {"success": False, "error": str(e)}


@app.get("/health")
def health():
    """Improved health check that verifies basic functionality"""
    try:
        # Simple database check (simulated)
        if not service.list_users():  # Assume this checks DB connection
            raise Exception("Database connection failed")
        
        # Basic config check
        ConfigModel(**config).dict()
        
        return {"status": "ok", "details": "All systems operational"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return PlainTextResponse("Service Unavailable", status_code=503)