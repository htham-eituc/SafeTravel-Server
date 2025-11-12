from fastapi import FastAPI
from dotenv import load_dotenv
import os
from database.database import Base, engine
from api import auth, users, friends, circles, circle_members
from models import user, circle, circle_member, location, notification, sos_alert, admin_log, friend

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(friends.router, prefix="/api", tags=["friends"])
app.include_router(circles.router, prefix="/api", tags=["circles"])
app.include_router(circle_members.router, prefix="/api", tags=["circle_members"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SafeTravel API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
