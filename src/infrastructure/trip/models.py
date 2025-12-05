from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.database.sql.database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    tripname = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    trip_type = Column(String(50), nullable=False) #change to enum later
    have_elderly = Column(Boolean, default=False)
    have_children = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="trips")