from sqlalchemy.orm import Session
from src.infrastructure.user.models import User
from sqlalchemy.orm import Session
from src.infrastructure.user.models import User
from src.domain.user.repository_interface import IUserRepository
from src.domain.user.entities import User as UserEntity
from typing import List, Optional
from bcrypt import hashpw, gensalt
from datetime import datetime

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, db: Session, user_id: int) -> Optional[UserEntity]:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            return UserEntity.model_validate(db_user.__dict__)
        return None

    def get_user_by_email(self, db: Session, email: str) -> Optional[UserEntity]:
        db_user = self.db.query(User).filter(User.email == email).first()
        if db_user:
            return UserEntity.model_validate(db_user.__dict__)
        return None

    def create_user(self, db: Session, user_data: UserEntity) -> UserEntity:
        # Mật khẩu đã được băm trong AuthUseCases, nên chỉ cần lưu trực tiếp
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone,
            avatar_url=user_data.avatar_url,
            hashed_password=user_data.hashed_password, # Sử dụng mật khẩu đã băm
            full_name=user_data.full_name,
            disabled=user_data.disabled,
            created_at=user_data.created_at
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserEntity.model_validate(db_user.__dict__)

    def update_user(self, db: Session, user_id: int, user_data: UserEntity) -> Optional[UserEntity]:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            update_data = user_data.model_dump(exclude_unset=True)
            if "hashed_password" in update_data:
                update_data["hashed_password"] = hashpw(update_data["hashed_password"].encode('utf-8'), gensalt()).decode('utf-8')
            for key, value in update_data.items():
                setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
            return UserEntity.model_validate(db_user.__dict__)
        return None

    def delete_user(self, db: Session, user_id: int) -> bool:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            db.commit()
            return True
        return False
