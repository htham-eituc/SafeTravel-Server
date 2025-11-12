from sqlalchemy.orm import Session
from .repository import UserRepository
from .schemas import UserCreate, UserUpdate
from typing import Optional
from .models import User
from bcrypt import checkpw
from datetime import datetime, timedelta
import jwt
from src.config.settings import get_settings

class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def get_user(self, user_id: int) -> User:
        return self.user_repo.get_user(user_id)

    def get_user_by_email(self, email: str) -> User:
        return self.user_repo.get_user_by_email(email)

    def create_user(self, user: UserCreate) -> User:
        return self.user_repo.create_user(user)

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        return self.user_repo.update_user(user_id, user_update)

    def delete_user(self, user_id: int) -> bool:
        return self.user_repo.delete_user(user_id)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.user_repo.get_user_by_email(email)
        if not user or not checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return None
        return user

    def create_access_token(self, user_id: int) -> str:
        settings = get_settings()
        to_encode = {"id": user_id, "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
