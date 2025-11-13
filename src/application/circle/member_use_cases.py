from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.circle.member_repository_interface import ICircleMemberRepository
from src.application.circle.member_dto import CircleMemberCreate, CircleMemberUpdate
from src.domain.circle.member_entities import CircleMember as CircleMemberEntity
from datetime import datetime

class CircleMemberUseCases:
    def __init__(self, circle_member_repository: ICircleMemberRepository):
        self.circle_member_repo = circle_member_repository

    def get_circle_member(self, db: Session, circle_member_id: int) -> Optional[CircleMemberEntity]:
        return self.circle_member_repo.get_circle_member(db, circle_member_id)

    def get_circle_members_by_circle(self, db: Session, circle_id: int) -> List[CircleMemberEntity]:
        return self.circle_member_repo.get_circle_members_by_circle(db, circle_id)

    def get_circle_members_by_member(self, db: Session, member_id: int) -> List[CircleMemberEntity]:
        return self.circle_member_repo.get_circle_members_by_member(db, member_id)

    def create_circle_member(self, db: Session, circle_member_data: CircleMemberCreate) -> CircleMemberEntity:
        circle_member_entity = CircleMemberEntity(
            circle_id=circle_member_data.circle_id,
            member_id=circle_member_data.member_id,
            role=circle_member_data.role,
            joined_at=datetime.now()
        )
        return self.circle_member_repo.create_circle_member(db, circle_member_entity)

    def update_circle_member(self, db: Session, circle_member_id: int, circle_member_update: CircleMemberUpdate) -> Optional[CircleMemberEntity]:
        existing_member = self.circle_member_repo.get_circle_member(db, circle_member_id)
        if not existing_member:
            return None
        
        update_data = circle_member_update.model_dump(exclude_unset=True)
        updated_member_entity = existing_member.model_copy(update=update_data)
        return self.circle_member_repo.update_circle_member(db, circle_member_id, updated_member_entity)

    def delete_circle_member(self, db: Session, circle_member_id: int) -> bool:
        return self.circle_member_repo.delete_circle_member(db, circle_member_id)
