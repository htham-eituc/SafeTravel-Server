from sqlalchemy.orm import Session
from .models import Circle
from .schemas import CircleCreate, CircleUpdate

class CircleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_circle(self, circle_id: int):
        return self.db.query(Circle).filter(Circle.id == circle_id).first()

    def get_circles_by_owner(self, owner_id: int):
        return self.db.query(Circle).filter(Circle.owner_id == owner_id).all()

    def create_circle(self, circle: CircleCreate, owner_id: int):
        print(f"DEBUG: self.db in create_circle: {type(self.db)}")
        db_circle = Circle(
            circle_name=circle.circle_name,
            description=circle.description,
            status=circle.status,
            owner_id=owner_id
        )
        self.db.add(db_circle)
        self.db.commit()
        self.db.refresh(db_circle)
        return db_circle

    def update_circle(self, circle_id: int, circle_update: CircleUpdate):
        db_circle = self.db.query(Circle).filter(Circle.id == circle_id).first()
        if db_circle:
            update_data = circle_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_circle, key, value)
            self.db.commit()
            self.db.refresh(db_circle)
        return db_circle

    def delete_circle(self, circle_id: int):
        db_circle = self.db.query(Circle).filter(Circle.id == circle_id).first()
        if db_circle:
            self.db.delete(db_circle)
            self.db.commit()
            return True
        return False
