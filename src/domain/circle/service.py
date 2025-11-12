from sqlalchemy.orm import Session
from .repository import CircleRepository
from .member_repository import CircleMemberRepository
from .schemas import CircleCreate, CircleUpdate
from .member_schemas import CircleMemberCreate
from .models import Circle

class CircleService:
    def __init__(self, circle_repository: CircleRepository, circle_member_repository: CircleMemberRepository):
        self.circle_repo = circle_repository
        self.circle_member_repo = circle_member_repository

    def get_circle(self, circle_id: int) -> Circle:
        return self.circle_repo.get_circle(circle_id)

    def get_circles_by_owner(self, owner_id: int) -> list[Circle]:
        return self.circle_repo.get_circles_by_owner(owner_id)

    def create_circle(self, circle: CircleCreate, owner_id: int) -> Circle:
        # Deactivate all existing active circles for the user
        active_circles = self.circle_repo.get_circles_by_owner(owner_id)
        for active_circle in active_circles:
            if active_circle.status == "active":
                self.circle_repo.update_circle(active_circle.id, CircleUpdate(status="inactive"))
        
        # Create the new circle
        new_circle = self.circle_repo.create_circle(circle, owner_id)

        # Add the owner as a member to the new circle
        circle_member_create = CircleMemberCreate(
            circle_id=new_circle.id,
            member_id=owner_id,
            role="owner"
        )
        self.circle_member_repo.create_circle_member(circle_member_create)

        return new_circle

    def update_circle(self, circle_id: int, circle_update: CircleUpdate) -> Circle:
        return self.circle_repo.update_circle(circle_id, circle_update)

    def delete_circle(self, circle_id: int) -> bool:
        return self.circle_repo.delete_circle(circle_id)
