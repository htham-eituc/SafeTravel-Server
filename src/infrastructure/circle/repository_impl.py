from sqlalchemy.orm import Session
from src.infrastructure.circle.models import Circle
from src.domain.circle.repository_interface import ICircleRepository
from src.domain.circle.entities import Circle as CircleEntity
from src.application.circle.dto import CircleCreate, CircleUpdate
from typing import List, Optional

class CircleRepository(ICircleRepository):
    def get_circle(self, db: Session, circle_id: int) -> Optional[CircleEntity]:
        db_circle = db.query(Circle).filter(Circle.id == circle_id).first()
        if db_circle:
            return CircleEntity.model_validate(db_circle.__dict__)
        return None

    def get_circles_by_owner(self, db: Session, owner_id: int) -> List[CircleEntity]:
        db_circles = db.query(Circle).filter(Circle.owner_id == owner_id).all()
        return [CircleEntity.model_validate(c.__dict__) for c in db_circles]

    def create_circle(self, db: Session, circle_data: CircleEntity) -> CircleEntity:
        db_circle = Circle(
            circle_name=circle_data.circle_name,
            description=circle_data.description,
            status=circle_data.status,
            owner_id=circle_data.owner_id
        )
        db.add(db_circle)
        db.commit()
        db.refresh(db_circle)
        return CircleEntity.model_validate(db_circle.__dict__)

    def update_circle(self, db: Session, circle_id: int, circle_data: CircleEntity) -> Optional[CircleEntity]:
        db_circle = db.query(Circle).filter(Circle.id == circle_id).first()
        if db_circle:
            for key, value in circle_data.model_dump(exclude_unset=True).items():
                setattr(db_circle, key, value)
            db.commit()
            db.refresh(db_circle)
            return CircleEntity.model_validate(db_circle.__dict__)
        return None

    def delete_circle(self, db: Session, circle_id: int) -> bool:
        db_circle = db.query(Circle).filter(Circle.id == circle_id).first()
        if db_circle:
            db.delete(db_circle)
            db.commit()
            return True
        return False
