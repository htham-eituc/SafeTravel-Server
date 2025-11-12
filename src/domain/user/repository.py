from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate, UserUpdate
from bcrypt import hashpw, gensalt

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user: UserCreate):
        hashed_password = hashpw(user.password.encode('utf-8'), gensalt()).decode('utf-8')
        db_user = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password_hash=hashed_password,
            avatar_url=user.avatar_url
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user_update: UserUpdate):
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            update_data = user_update.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["password_hash"] = hashpw(update_data["password"].encode('utf-8'), gensalt()).decode('utf-8')
                del update_data["password"]
            for key, value in update_data.items():
                setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int):
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
