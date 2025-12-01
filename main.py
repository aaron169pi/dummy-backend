python
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from service import UserService
from utils import load_config, Logger, validate_age
import os
import time

app = FastAPI()
logger = Logger("app.log")

CONFIG_FILE = "settings.json"
config_last_modified = 0
config_data = {}

def get_config():
    global config_data, config_last_modified
    
    try:
        current_modified = os.path.getmtime(CONFIG_FILE)
        if current_modified != config_last_modified:
            config_data = load_config(CONFIG_FILE)
            config_last_modified = current_modified
            
        return config_data.copy()
        
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        return {}

class UserCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up")
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        execution_time = time.time() - start_time
        
        logger.info(
            f"Incoming request: {request.method} {request.url.path} "
            f"Status: {response.status_code} Time: {execution_time:.3f}s"
        )
        return response
        
    except Exception as e:
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"Error: {str(e)}"
        )
        raise

@app.get("/users")
def list_users(service: UserService = Depends()):
    try:
        users = service.list_users()
        return {"users": users, "count": len(users)}
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching users"
        )

@app.get("/users/{user_id}")
def get_user(user_id: int, service: UserService = Depends()):
    user = service.get_user(user_id)
    if not user:
        logger.warning(f"User not found - ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

@app.post("/users")
def create_user(payload: UserCreateModel, service: UserService = Depends()):
    try:
        validated_data = payload.dict()
        user = service.create_user(**validated_data)
        logger.info(f"Created user - ID: {user['id']}, Name: {user['name']}")
        return {"created": user}
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error while creating user: {str(e)}"
        )

@app.get("/discount/{user_id}")
def discount(user_id: int, service: UserService = Depends()):
    try:
        config = get_config()
        discount_rate = config.get("discount_rate", 0.1)
        age_threshold = config.get("age_threshold", 40)
        
        if discount_rate <= 0:
            discount_rate = 0.01  # Minimum 0.01% discount
            
        value = service.calculate_discount(user_id=user_id)
        logger.info(
            f"Calculated discount - User: {user_id}, Value: {value}, "
            f"Rate: {discount_rate}, AgeThreshold: {age_threshold}"
        )
        return {"discount": value, "rate": discount_rate}
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Discount error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error calculating discount: {str(e)}"
        )

@app.get("/config")
def read_config():
    try:
        config = get_config()
        filtered_config = {
            key: value 
            for key, value in config.items()
            if key in ["version", "discount_rate", "age_threshold"]
        }
        return {"config": filtered_config}
        
    except Exception as e:
        logger.error(f"Config reading error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal error reading configuration"
        )

@app.get("/health")
def health():
    try:
        config = get_config()
        return {
            "status": "ok",
            "version": config.get("version", "unknown"),
            "timestamp": int(time.time())
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "details": str(e)}
        )