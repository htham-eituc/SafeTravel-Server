from fastapi import FastAPI
from dotenv import load_dotenv
import os
from src.domain.database.database import Base, engine
# # from src.presentation.routers import auth, users, friends, circles, circle_members
# from src.domain.user import user
# from src.domain.circle import circle, circle_member
# from src.domain.location import location
# from src.domain.notification import notification
# from src.domain.sos_alert import sos_alert
# from src.domain.admin_log import admin_log
# from src.domain.friend import friend

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

# app.include_router(auth.router, prefix="/api", tags=["auth"])
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
