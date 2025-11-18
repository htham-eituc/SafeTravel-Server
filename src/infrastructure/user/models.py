from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.database.sql.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), nullable=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255), nullable=True)
    disabled = Column(Boolean, default=False)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    circles = relationship("Circle", back_populates="owner")
    circle_members = relationship("CircleMember", back_populates="member")
    locations = relationship("Location", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    sos_alerts = relationship("SOSAlert", back_populates="user")
    admin_logs = relationship("AdminLog", back_populates="admin")
    sent_friend_requests = relationship("FriendRequest", foreign_keys="[FriendRequest.sender_id]", back_populates="sender")
    received_friend_requests = relationship("FriendRequest", foreign_keys="[FriendRequest.receiver_id]", back_populates="receiver")
    friendships_as_user = relationship("Friendship", foreign_keys="[Friendship.user_id]", back_populates="user")
    friendships_as_friend = relationship("Friendship", foreign_keys="[Friendship.friend_id]", back_populates="friend")
