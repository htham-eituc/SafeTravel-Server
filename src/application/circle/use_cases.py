from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.circle.repository_interface import ICircleRepository
from src.domain.circle.entities import Circle as CircleEntity
from src.application.circle.dto import CircleCreate, CircleUpdate
from src.domain.circle.member_repository_interface import ICircleMemberRepository # Assuming this will be created
from src.domain.circle.member_entities import CircleMember as CircleMemberEntity # Assuming this will be created

class CircleUseCases:
    def __init__(self, circle_repository: ICircleRepository, circle_member_repository: ICircleMemberRepository):
        self.circle_repo = circle_repository
        self.circle_member_repo = circle_member_repository

    def get_circle(self, db: Session, circle_id: int) -> Optional[CircleEntity]:
        return self.circle_repo.get_circle(db, circle_id)

    def get_circles_by_owner(self, db: Session, owner_id: int) -> List[CircleEntity]:
        return self.circle_repo.get_circles_by_owner(db, owner_id)

    def create_circle(self, db: Session, circle_data: CircleCreate, owner_id: int) -> CircleEntity:
        # Deactivate all existing active circles for the user
        active_circles = self.circle_repo.get_circles_by_owner(db, owner_id)
        for active_circle in active_circles:
            if active_circle.status == "active":
                updated_circle_entity = active_circle.model_copy(update={"status": "inactive"})
                self.circle_repo.update_circle(db, active_circle.id, updated_circle_entity)
        
        # Create the new circle
        circle_entity = CircleEntity(
            circle_name=circle_data.circle_name,
            description=circle_data.description,
            status="active", # Default status
            owner_id=owner_id
        )
        new_circle = self.circle_repo.create_circle(db, circle_entity)

        # Add the owner as a member to the new circle
        circle_member_entity = CircleMemberEntity(
            circle_id=new_circle.id,
            member_id=owner_id,
            role="owner"
        )
        self.circle_member_repo.create_circle_member(db, circle_member_entity)

        return new_circle

    def update_circle(self, db: Session, circle_id: int, circle_update: CircleUpdate) -> Optional[CircleEntity]:
        existing_circle = self.circle_repo.get_circle(db, circle_id)
        if not existing_circle:
            return None
        
        update_data = circle_update.model_dump(exclude_unset=True)
        updated_circle_entity = existing_circle.model_copy(update=update_data)
        return self.circle_repo.update_circle(db, circle_id, updated_circle_entity)

    def delete_circle(self, db: Session, circle_id: int) -> bool:
        return self.circle_repo.delete_circle(db, circle_id)
