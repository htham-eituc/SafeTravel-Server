from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.database.sql.database import Base

class Circle(Base):
    __tablename__ = "circles"

    id = Column(Integer, primary_key=True, index=True)
    circle_name = Column(String(255), index=True)
    description = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50), default="active") # e.g., "active", "inactive", "archived"
    created_at = Column(DateTime, server_default=func.now())

    owner = relationship("User", back_populates="circles")
    members = relationship("CircleMember", back_populates="circle")
    sos_alerts = relationship("SOSAlert", back_populates="circle")
