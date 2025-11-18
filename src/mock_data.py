from sqlalchemy.orm import Session
from src.infrastructure.database.sql.database import Base, engine, get_db
from src.infrastructure.user.models import User
from src.application.user.dto import UserCreate
from src.infrastructure.user.repository_impl import UserRepository
from src.infrastructure.circle.models import Circle
from src.application.circle.dto import CircleCreate
from src.infrastructure.circle.repository_impl import CircleRepository
from src.infrastructure.circle.member_models import CircleMember
from src.application.circle.member_dto import CircleMemberCreate
from src.infrastructure.circle.member_repository_impl import CircleMemberRepository
from src.infrastructure.friend.models import Friend
from src.application.friend.dto import FriendCreate
from src.infrastructure.friend.repository_impl import FriendRepository
from src.infrastructure.location.models import Location
from src.application.location.dto import LocationCreate
from src.infrastructure.location.repository_impl import LocationRepository
from src.infrastructure.notification.models import Notification
from src.application.notification.dto import NotificationCreate
from src.infrastructure.notification.repository_impl import NotificationRepository
from src.infrastructure.admin_log.models import AdminLog
from src.application.admin_log.dto import AdminLogCreate
from src.infrastructure.admin_log.repository_impl import AdminLogRepository
from bcrypt import hashpw, gensalt
from datetime import datetime, timedelta

def create_mock_data(db: Session):
    print("Creating mock data...")

    # Create Users
    user_repo = UserRepository(db)
    
    user1_data = UserCreate(name="Alice Smith", email="alice@example.com", phone="1112223333", password="password123", avatar_url="http://example.com/alice.jpg")
    user1 = user_repo.create_user(user1_data)

    user2_data = UserCreate(name="Bob Johnson", email="bob@example.com", phone="4445556666", password="password123", avatar_url="http://example.com/bob.jpg")
    user2 = user_repo.create_user(user2_data)

    user3_data = UserCreate(name="Charlie Brown", email="charlie@example.com", phone="7778889999", password="password123", avatar_url="http://example.com/charlie.jpg")
    user3 = user_repo.create_user(user3_data)

    print(f"Created users: {user1.email}, {user2.email}, {user3.email}")

    # Create Circles
    circle_repo = CircleRepository(db)
    
    circle1_data = CircleCreate(circle_name="Family", description="Close family members")
    circle1 = circle_repo.create_circle(circle1_data, user1.id)

    circle2_data = CircleCreate(circle_name="Friends", description="My closest friends")
    circle2 = circle_repo.create_circle(circle2_data, user2.id)

    print(f"Created circles: {circle1.circle_name}, {circle2.circle_name}")

    # Add Circle Members
    circle_member_repo = CircleMemberRepository(db)
    
    circle_member_repo.create_circle_member(CircleMemberCreate(circle_id=circle1.id, member_id=user2.id, role="member"))
    circle_member_repo.create_circle_member(CircleMemberCreate(circle_id=circle1.id, member_id=user3.id, role="member"))
    circle_member_repo.create_circle_member(CircleMemberCreate(circle_id=circle2.id, member_id=user1.id, role="member"))

    print("Added circle members.")

    # Create Friends
    friend_repo = FriendRepository(db)
    
    friend_repo.create_friend(db, FriendCreate(user_id=user1.id, friend_id=user2.id))
    friend_repo.create_friend(db, FriendCreate(user_id=user2.id, friend_id=user1.id)) # Bidirectional
    friend_repo.create_friend(db, FriendCreate(user_id=user1.id, friend_id=user3.id))

    print("Created friend relationships.")

    # Create Locations
    location_repo = LocationRepository(db)
    
    location_repo.create_location(LocationCreate(user_id=user1.id, latitude=34.052235, longitude=-118.243683, speed=10.5, accuracy=5.0))
    location_repo.create_location(LocationCreate(user_id=user2.id, latitude=34.052235, longitude=-118.243683, speed=12.0, accuracy=4.5))

    print("Created locations.")

    # Create Notifications
    notification_repo = NotificationRepository(db)
    
    notification_repo.create_notification(NotificationCreate(user_id=user1.id, title="Welcome!", message="Welcome to SafeTravel!", type="system"))
    notification_repo.create_notification(NotificationCreate(user_id=user2.id, title="New Friend Request", message="Alice sent you a friend request.", type="friend_request"))

    print("Created notifications.")


    # Create Admin Logs
    admin_log_repo = AdminLogRepository(db)
    
    admin_log_repo.create_admin_log(AdminLogCreate(admin_id=user1.id, action="user_created", target_id=user2.id))
    admin_log_repo.create_admin_log(AdminLogCreate(admin_id=user1.id, action="circle_created", target_id=circle1.id))

    print("Created admin logs.")
    print("Mock data creation complete.")

if __name__ == "__main__":
    # This block is for testing the mock data creation independently
    # In the actual application, create_mock_data will be called via a dependency.
    db_session = next(get_db())
    try:
        create_mock_data(db_session)
    finally:
        db_session.close()
