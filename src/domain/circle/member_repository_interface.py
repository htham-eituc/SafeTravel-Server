from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.circle.member_entities import CircleMember as CircleMemberEntity

class ICircleMemberRepository(ABC):
    @abstractmethod
    def get_circle_member(self, db: Session, circle_member_id: int) -> Optional[CircleMemberEntity]:
        pass

    @abstractmethod
    def get_circle_members_by_circle(self, db: Session, circle_id: int) -> List[CircleMemberEntity]:
        pass

    @abstractmethod
    def get_circle_members_by_member(self, db: Session, member_id: int) -> List[CircleMemberEntity]:
        pass

    @abstractmethod
    def create_circle_member(self, db: Session, circle_member_data: CircleMemberEntity) -> CircleMemberEntity:
        pass

    @abstractmethod
    def update_circle_member(self, db: Session, circle_member_id: int, circle_member_data: CircleMemberEntity) -> Optional[CircleMemberEntity]:
        pass

    @abstractmethod
    def delete_circle_member(self, db: Session, circle_member_id: int) -> bool:
        pass
