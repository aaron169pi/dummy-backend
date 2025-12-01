from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from service import UserService
from utils import load_config, Logger

app = FastAPI()
logger = Logger("app.log")

# Load config globally (Issue: no reload, no fallback)
config = load_config("settings.json")

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
        raise HTTPException(status_code=500, detail="Internal error")


@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


@app.post("/users")
def create_user(payload: dict):
    # Issue: No Pydantic validation
    name = payload.get("name")
    age = payload.get("age")

    if not name:
        raise HTTPException(status_code=400, detail="Missing name")

    user = service.create_user(name=name, age=age)
    return {"created": user}


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
    # Issue: returns sensitive config details
    return config


@app.get("/health")
def health():
    # Issue: Does not check DB or dependencies
    return {"status": "ok"}

