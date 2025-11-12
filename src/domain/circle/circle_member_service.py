from sqlalchemy.orm import Session
from .circle_member_repository import CircleMemberRepository
from .circle_member_schema import CircleMemberCreate, CircleMemberUpdate
from .circle_member import CircleMember

class CircleMemberService:
    def __init__(self, circle_member_repository: CircleMemberRepository):
        self.circle_member_repo = circle_member_repository

    def get_circle_member(self, circle_member_id: int) -> CircleMember:
        return self.circle_member_repo.get_circle_member(circle_member_id)

    def get_circle_members_by_circle(self, circle_id: int) -> list[CircleMember]:
        return self.circle_member_repo.get_circle_members_by_circle(circle_id)

    def get_circle_members_by_member(self, member_id: int) -> list[CircleMember]:
        return self.circle_member_repo.get_circle_members_by_member(member_id)

    def create_circle_member(self, circle_member: CircleMemberCreate) -> CircleMember:
        return self.circle_member_repo.create_circle_member(circle_member)

    def update_circle_member(self, circle_member_id: int, circle_member_update: CircleMemberUpdate) -> CircleMember:
        return self.circle_member_repo.update_circle_member(circle_member_id, circle_member_update)

    def delete_circle_member(self, circle_member_id: int) -> bool:
        return self.circle_member_repo.delete_circle_member(circle_member_id)
