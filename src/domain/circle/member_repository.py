from sqlalchemy.orm import Session
from .member_models import CircleMember
from .member_schemas import CircleMemberCreate, CircleMemberUpdate

class CircleMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_circle_member(self, circle_member_id: int):
        return self.db.query(CircleMember).filter(CircleMember.id == circle_member_id).first()

    def get_circle_members_by_circle(self, circle_id: int):
        return self.db.query(CircleMember).filter(CircleMember.circle_id == circle_id).all()

    def get_circle_members_by_member(self, member_id: int):
        return self.db.query(CircleMember).filter(CircleMember.member_id == member_id).all()

    def create_circle_member(self, circle_member: CircleMemberCreate):
        print(f"DEBUG: self.db in create_circle_member: {type(self.db)}")
        db_circle_member = CircleMember(
            circle_id=circle_member.circle_id,
            member_id=circle_member.member_id,
            role=circle_member.role
        )
        self.db.add(db_circle_member)
        self.db.commit()
        self.db.refresh(db_circle_member)
        return db_circle_member

    def update_circle_member(self, circle_member_id: int, circle_member_update: CircleMemberUpdate):
        db_circle_member = self.db.query(CircleMember).filter(CircleMember.id == circle_member_id).first()
        if db_circle_member:
            update_data = circle_member_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_circle_member, key, value)
            self.db.commit()
            self.db.refresh(db_circle_member)
        return db_circle_member

    def delete_circle_member(self, circle_member_id: int):
        db_circle_member = self.db.query(CircleMember).filter(CircleMember.id == circle_member_id).first()
        if db_circle_member:
            self.db.delete(db_circle_member)
            self.db.commit()
            return True
        return False
