from sqlalchemy.orm import Session
from src.infrastructure.user.models import User
from src.domain.user.repository_interface import IUserRepository
from src.domain.user.entities import User as UserEntity
from src.application.user.dto import UserCreate, UserUpdate
from typing import List, Optional
from bcrypt import hashpw, gensalt
from datetime import datetime

class UserRepository(IUserRepository):
    def get_user(self, db: Session, user_id: int) -> Optional[UserEntity]:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            return UserEntity.model_validate(db_user.__dict__)
        return None

    def get_user_by_email(self, db: Session, email: str) -> Optional[UserEntity]:
        db_user = db.query(User).filter(User.email == email).first()
        if db_user:
            return UserEntity.model_validate(db_user.__dict__)
        return None

    def create_user(self, db: Session, user_data: UserEntity) -> UserEntity:
        hashed_password = hashpw(user_data.hashed_password.encode('utf-8'), gensalt()).decode('utf-8')
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            disabled=user_data.disabled,
            created_at=user_data.created_at
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserEntity.model_validate(db_user.__dict__)

    def update_user(self, db: Session, user_id: int, user_data: UserEntity) -> Optional[UserEntity]:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            update_data = user_data.model_dump(exclude_unset=True)
            if "hashed_password" in update_data:
                update_data["hashed_password"] = hashpw(update_data["hashed_password"].encode('utf-8'), gensalt()).decode('utf-8')
            for key, value in update_data.items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
            return UserEntity.model_validate(db_user.__dict__)
        return None

    def delete_user(self, db: Session, user_id: int) -> bool:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False
