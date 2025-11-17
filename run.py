from fastapi import FastAPI
from dotenv import load_dotenv
import os
from src.presentation.auth_routes import router as auth_router
from src.infrastructure.database.sql.database import create_db_and_tables # Import for DB creation
import src.infrastructure # Import the infrastructure package to load all models

load_dotenv()
app = FastAPI()

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth_router, prefix="/api", tags=["auth"])
# app.include_router(users.router, prefix="/api", tags=["users"])
# app.include_router(friends.router, prefix="/api", tags=["friends"])
# app.include_router(circles.router, prefix="/api", tags=["circles"])
# app.include_router(circle_members.router, prefix="/api", tags=["circle_members"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SafeTravel API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
