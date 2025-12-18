import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Cấu hình & Database
from src.config.settings import get_settings
from src.infrastructure.database.sql.database import create_db_and_tables
import src.infrastructure  # Đảm bảo các Model được nạp

# Import Routers
from src.presentation import (
    auth_routes, friend_routes, sos_routes, circle_routes,
    notification_routes, admin_log_routes, user_routes,
    ai_routes, trip_routes, news_incident_routes, incident_routes
)

load_dotenv()
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chỉ tự động tạo bảng khi ở môi trường development
    if settings.ENVIRONMENT == "development":
        print(f"--- [ENV: {settings.ENVIRONMENT}] Khởi tạo database và bảng ---")
        # create_db_and_tables()
    yield
    print(f"--- [ENV: {settings.ENVIRONMENT}] Đang tắt ứng dụng ---")

def create_app() -> FastAPI:
    app = FastAPI(
        title="SafeTravel API",
        description="Hệ thống hỗ trợ du lịch an toàn",
        version="1.0.0",
        lifespan=lifespan,
        # Ẩn docs nếu ở production để tăng tính bảo mật
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url=None
    )

    # Cấu hình CORS
    # Trong thực tế deploy, hãy thay ["*"] bằng domain cụ thể của bạn
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Đăng ký các Router theo cấu trúc danh sách để dễ quản lý
    routers = [
        (auth_routes.router, "auth"),
        (friend_routes.router, "friends"),
        (sos_routes.router, "sos"),
        (circle_routes.router, "circles"),
        (notification_routes.router, "notifications"),
        (admin_log_routes.router, "admin_logs"),
        (user_routes.router, "users"),
        (ai_routes.router, "ai"),
        (trip_routes.router, "trips"),
        (news_incident_routes.router, "news_incidents"),
        (incident_routes.router, "incidents"),
    ]

    for router, tag in routers:
        app.include_router(router, prefix="/api", tags=[tag])

    @app.get("/", tags=["Root"])
    def read_root():
        return {
            "message": "Welcome to SafeTravel API!",
            "status": "online",
            "environment": settings.ENVIRONMENT
        }
    
    return app

app = create_app()

if __name__ == "__main__":
    # Khi chạy trực tiếp: python run.py
    port = int(os.getenv("PORT", 8000))
    if settings.ENVIRONMENT == "development":
        uvicorn.run("run:app", host="0.0.0.0", port=port, reload=True)
    else:
        # Chế độ này chỉ dùng để test nhanh Prod trên máy cá nhân
        uvicorn.run("run:app", host="0.0.0.0", port=port, workers=4)