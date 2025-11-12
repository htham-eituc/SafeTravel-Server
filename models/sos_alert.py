from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base
import enum

class SOSStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    RESOLVED = "resolved"

class SOSAlert(Base):
    __tablename__ = "sos_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    circle_id = Column(Integer, ForeignKey("circles.id"), nullable=True) # New field
    latitude = Column(Float)
    longitude = Column(Float)
    message = Column(String(255), nullable=True)
    status = Column(Enum(SOSStatus), default=SOSStatus.PENDING) # Changed to Enum
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sos_alerts")
    circle = relationship("Circle", back_populates="sos_alerts")
