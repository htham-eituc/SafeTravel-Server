from sqlalchemy.orm import Session
from src.infrastructure.database.sql.database import Base, engine, get_db
from src.domain.user.user import User
from src.domain.user.user_schema import UserCreate
from src.domain.user.user_repository import UserRepository
from src.domain.circle.circle import Circle
from src.domain.circle.circle_schema import CircleCreate
from src.domain.circle.circle_repository import CircleRepository
from src.domain.circle.circle_member import CircleMember
from src.domain.circle.circle_member_schema import CircleMemberCreate
from src.domain.circle.circle_member_repository import CircleMemberRepository
from src.domain.friend.friend import Friend
from src.domain.friend.friend_schema import FriendCreate
from src.domain.friend.friend_repository import FriendRepository
from src.domain.location.location import Location
from src.domain.location.location_schema import LocationCreate
from src.domain.location.location_repository import LocationRepository
from src.domain.notification.notification import Notification
from src.domain.notification.notification_schema import NotificationCreate
from src.domain.notification.notification_repository import NotificationRepository
from src.domain.admin_log.admin_log import AdminLog
from src.domain.admin_log.admin_log_schema import AdminLogCreate
from src.domain.admin_log.admin_log_repository import AdminLogRepository
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
