from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.infrastructure.database.sql.database import Base

class CircleMember(Base):
    __tablename__ = "circle_members"

    id = Column(Integer, primary_key=True, index=True)
    circle_id = Column(Integer, ForeignKey("circles.id"))
    member_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String(50))

    circle = relationship("Circle", back_populates="members")
    member = relationship("User", back_populates="circle_members")
