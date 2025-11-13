from sqlalchemy.orm import Session
from src.infrastructure.circle.member_models import CircleMember
from src.domain.circle.member_repository_interface import ICircleMemberRepository
from src.domain.circle.member_entities import CircleMember as CircleMemberEntity
from src.application.circle.member_dto import CircleMemberCreate, CircleMemberUpdate
from typing import List, Optional
from datetime import datetime

class CircleMemberRepository(ICircleMemberRepository):
    def get_circle_member(self, db: Session, circle_member_id: int) -> Optional[CircleMemberEntity]:
        db_circle_member = db.query(CircleMember).filter(CircleMember.id == circle_member_id).first()
        if db_circle_member:
            return CircleMemberEntity.model_validate(db_circle_member.__dict__)
        return None

    def get_circle_members_by_circle(self, db: Session, circle_id: int) -> List[CircleMemberEntity]:
        db_circle_members = db.query(CircleMember).filter(CircleMember.circle_id == circle_id).all()
        return [CircleMemberEntity.model_validate(cm.__dict__) for cm in db_circle_members]

    def get_circle_members_by_member(self, db: Session, member_id: int) -> List[CircleMemberEntity]:
        db_circle_members = db.query(CircleMember).filter(CircleMember.member_id == member_id).all()
        return [CircleMemberEntity.model_validate(cm.__dict__) for cm in db_circle_members]

    def create_circle_member(self, db: Session, circle_member_data: CircleMemberEntity) -> CircleMemberEntity:
        db_circle_member = CircleMember(
            circle_id=circle_member_data.circle_id,
            member_id=circle_member_data.member_id,
            role=circle_member_data.role
        )
        db.add(db_circle_member)
        db.commit()
        db.refresh(db_circle_member)
        return CircleMemberEntity.model_validate(db_circle_member.__dict__)

    def update_circle_member(self, db: Session, circle_member_id: int, circle_member_data: CircleMemberEntity) -> Optional[CircleMemberEntity]:
        db_circle_member = db.query(CircleMember).filter(CircleMember.id == circle_member_id).first()
        if db_circle_member:
            for key, value in circle_member_data.model_dump(exclude_unset=True).items():
                setattr(db_circle_member, key, value)
            db.commit()
            db.refresh(db_circle_member)
            return CircleMemberEntity.model_validate(db_circle_member.__dict__)
        return None

    def delete_circle_member(self, db: Session, circle_member_id: int) -> bool:
        db_circle_member = db.query(CircleMember).filter(CircleMember.id == circle_member_id).first()
        if db_circle_member:
            db.delete(db_circle_member)
            db.commit()
            return True
        return False
