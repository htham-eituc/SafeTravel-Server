from sqlalchemy import Column, Integer, String, DateTime, ForeignKey # Re-added Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.database.sql.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) # Changed back to Integer
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255))
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    circles = relationship("Circle", back_populates="owner")
    circle_members = relationship("CircleMember", back_populates="member")
    locations = relationship("Location", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    sos_alerts = relationship("SOSAlert", back_populates="user")
    admin_logs = relationship("AdminLog", back_populates="admin")
    friends = relationship("Friend", foreign_keys="[Friend.user_id]", back_populates="user")
    friend_of = relationship("Friend", foreign_keys="[Friend.friend_id]", back_populates="friend")
