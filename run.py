from fastapi import FastAPI
from dotenv import load_dotenv
import os
from src.domain.database.database import Base, engine
# from src.tests.mock_db_test import run_mock_db_test
from src.domain.user import models as user_models
from src.domain.circle import models as circle_models
from src.domain.circle import member_models as circle_member_models
from src.domain.location import models as location_models
from src.domain.notification import models as notification_models
from src.domain.admin_log import models as admin_log_models
from src.domain.friend import models as friend_models

load_dotenv()

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
