from sqlalchemy.orm import Session
from src.infrastructure.user.models import User
from src.domain.user.repository_interface import UserRepositoryInterface
from src.domain.user.entities import User as UserEntity
from typing import Optional
from datetime import datetime

class UserRepositoryImpl(UserRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[UserEntity]: # Changed to int
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            return UserEntity.model_validate(db_user)
        return None

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        db_user = self.db.query(User).filter(User.email == email).first()
        if db_user:
            return UserEntity.model_validate(db_user)
        return None

    def create(self, user_data: UserEntity) -> UserEntity:
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=user_data.password_hash, # Changed to password_hash
            phone=user_data.phone,
            avatar_url=user_data.avatar_url,
            created_at=datetime.now() # Set created_at here or rely on DB default
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserEntity.model_validate(db_user)

    def update(self, user_id: int, user_data: UserEntity) -> Optional[UserEntity]: # Changed to int
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            update_data = user_data.model_dump(exclude_unset=True, exclude={"id", "created_at"})
            if "password_hash" in update_data: # Check for password_hash
                # In a real app, you might re-hash the password here if it's being updated
                pass 
            for key, value in update_data.items():
                setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
            return UserEntity.model_validate(db_user)
        return None

    def delete(self, user_id: int) -> bool: # Changed to int
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
