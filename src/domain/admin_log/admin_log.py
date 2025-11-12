from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.database import Base

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255))
    target_id = Column(Integer, nullable=True) # ID of the entity that was acted upon
    created_at = Column(DateTime, server_default=func.now())

    admin = relationship("User", back_populates="admin_logs")
