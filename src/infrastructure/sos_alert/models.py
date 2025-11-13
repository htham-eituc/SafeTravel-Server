from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.database import Base

class SOSAlert(Base):
    __tablename__ = "sos_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    circle_id = Column(Integer, ForeignKey("circles.id"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    message = Column(String(255), nullable=True)
    status = Column(String(50), default="pending") # e.g., "pending", "resolved", "false_alarm"
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sos_alerts")
    circle = relationship("Circle", back_populates="sos_alerts")
