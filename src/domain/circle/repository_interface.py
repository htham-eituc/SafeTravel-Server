from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.circle.entities import Circle as CircleEntity

class ICircleRepository(ABC):
    @abstractmethod
    def get_circle(self, db: Session, circle_id: int) -> Optional[CircleEntity]:
        pass

    @abstractmethod
    def get_circles_by_owner(self, db: Session, owner_id: int) -> List[CircleEntity]:
        pass

    @abstractmethod
    def create_circle(self, db: Session, circle_data: CircleEntity) -> CircleEntity:
        pass

    @abstractmethod
    def update_circle(self, db: Session, circle_id: int, circle_data: CircleEntity) -> Optional[CircleEntity]:
        pass

    @abstractmethod
    def delete_circle(self, db: Session, circle_id: int) -> bool:
        pass

    @abstractmethod
    def get_active_circle_by_owner_id(self, db: Session, owner_id: int) -> Optional[CircleEntity]:
        pass
