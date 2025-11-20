from fastapi import FastAPI
from dotenv import load_dotenv
import os
from src.presentation.auth_routes import router as auth_router
from src.presentation.friend_routes import router as friend_router
from src.presentation.sos_routes import router as sos_router
from src.presentation.circle_routes import router as circle_router # Import circle_router
from src.presentation.notification_routes import router as notification_router
from src.presentation.admin_log_routes import router as admin_log_router
from src.infrastructure.database.sql.database import create_db_and_tables # Import for DB creation
import src.infrastructure # Import the infrastructure package to load all models
from contextlib import asynccontextmanager

load_dotenv()

from src.config.settings import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == "development":
        create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(friend_router, prefix="/api", tags=["friends"])
app.include_router(sos_router, prefix="/api", tags=["sos"])
app.include_router(circle_router, prefix="/api", tags=["circles"]) # Include circle_router
app.include_router(notification_router, prefix="/api", tags=["notifications"])
app.include_router(admin_log_router, prefix="/api", tags=["admin_logs"])
# app.include_router(users.router, prefix="/api", tags=["users"])
# app.include_router(circles.router, prefix="/api", tags=["circles"])
# app.include_router(circle_members.router, prefix="/api", tags=["circle_members"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SafeTravel API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
