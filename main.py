python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from service import UserService
from utils import load_config, Logger, ConfigSchema

app = FastAPI()
logger = Logger("app.log")

# Initialize config with validation and fallback
try:
    config = load_config("settings.json")
except Exception as e:
    logger.error(f"Failed to load config: {e}")
    config = {}

class Config(BaseModel):
    discount_rate: float = 0.1
    age_threshold: int = 40
    
validated_config = Config(**config)

service = UserService(config=validated_config.dict(), logger=logger)

@app.get("/config")
def read_config():
    """Get filtered configuration"""
    filtered_config = {
        "discount_rate": config.get("discount_rate"),
        "age_threshold": config.get("age_threshold")
    }
    return JSONResponse(content=filtered_config)

@app.get("/health")
def health():
    """Check system health with dependency checks"""
    try:
        service.get_user(1)  # Simple check
        return {"status": "ok", "config_valid": bool(validated_config)}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "details": str(e)}
        )