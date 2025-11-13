from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.user.repository_interface import IUserRepository
from src.application.user.dto import UserCreate, UserUpdate
from src.domain.user.entities import User as UserEntity
from bcrypt import checkpw, hashpw, gensalt
from datetime import datetime, timedelta
import jwt
from src.config.settings import get_settings

class UserUseCases:
    def __init__(self, user_repository: IUserRepository):
        self.user_repo = user_repository

    def get_user(self, db: Session, user_id: int) -> Optional[UserEntity]:
        return self.user_repo.get_user(db, user_id)

    def get_user_by_email(self, db: Session, email: str) -> Optional[UserEntity]:
        return self.user_repo.get_user_by_email(db, email)

    def create_user(self, db: Session, user_data: UserCreate) -> UserEntity:
        hashed_password = hashpw(user_data.password.encode('utf-8'), gensalt()).decode('utf-8')
        user_entity = UserEntity(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            disabled=False, # Default value
            created_at=datetime.now()
        )
        return self.user_repo.create_user(db, user_entity)

    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserEntity]:
        existing_user = self.user_repo.get_user(db, user_id)
        if not existing_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = hashpw(update_data["password"].encode('utf-8'), gensalt()).decode('utf-8')
            del update_data["password"]
        
        updated_user_entity = existing_user.model_copy(update=update_data)
        return self.user_repo.update_user(db, user_id, updated_user_entity)

    def delete_user(self, db: Session, user_id: int) -> bool:
        return self.user_repo.delete_user(db, user_id)

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[UserEntity]:
        user = self.user_repo.get_user_by_email(db, email)
        if not user or not checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            return None
        return user

    def create_access_token(self, user_id: int) -> str:
        settings = get_settings()
        to_encode = {"id": user_id, "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
