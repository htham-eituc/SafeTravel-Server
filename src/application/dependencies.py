from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from src.application.trip.use_cases import TripUseCases
from src.application.security.security_interfaces import IPasswordHasher, ITokenService
from src.application.user.auth_use_cases import (
    LoginUserUseCase,
    RegisterUserUseCase,
    LogoutUserUseCase
)
from src.domain.user.repository_interface import IUserRepository
from src.infrastructure.database.sql.database import get_db
from src.infrastructure.security.security_impl import BcryptPasswordHasher, JwtTokenService
from src.infrastructure.user.repository_impl import UserRepository
from src.application.user.dto import TokenData
from src.domain.friend.repository_interface import IFriendRepository
from src.infrastructure.friend.repository_impl import FriendRepository
from src.application.friend.use_cases import FriendUseCases
from src.domain.user.entities import User as UserEntity
from src.domain.sos_alert.repository_interface import ISOSAlertRepository
from src.infrastructure.sos_alert.repository_impl import SOSAlertRepository
from src.application.sos_alert.use_cases import SOSAlertUseCases # Import SOSAlertUseCases
from src.domain.notification.repository_interface import INotificationRepository
from src.infrastructure.notification.repository_impl import NotificationRepository
from src.application.notification.use_cases import NotificationUseCases
from src.domain.admin_log.repository_interface import IAdminLogRepository
from src.infrastructure.admin_log.repository_impl import AdminLogRepository
from src.application.admin_log.use_cases import AdminLogUseCases
from src.domain.circle.repository_interface import ICircleRepository # Import ICircleRepository
from src.infrastructure.circle.repository_impl import CircleRepository # Import CircleRepository
from src.domain.circle.member_repository_interface import ICircleMemberRepository # Import ICircleMemberRepository
from src.infrastructure.circle.member_repository_impl import CircleMemberRepository # Import CircleMemberRepository
from src.application.circle.use_cases import CircleUseCases # Import CircleUseCases
from src.domain.news_incident.repository_interface import INewsIncidentRepository
from src.infrastructure.news_incident.repository_impl import NewsIncidentRepository
from src.application.news_incident.use_cases import NewsIncidentUseCases
from src.domain.user_report_incident.repository_interface import IUserReportIncidentRepository
from src.infrastructure.user_report_incident.repository_impl import UserReportIncidentRepository
from src.application.user_report_incident.use_cases import UserReportIncidentUseCases

def get_db_session() -> Session:
    yield from get_db()

def get_user_repository_impl(db: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)

def get_friend_repository_impl(db: Session = Depends(get_db_session)) -> FriendRepository:
    return FriendRepository()

def get_friend_use_cases(
    friend_repo: IFriendRepository = Depends(get_friend_repository_impl)
) -> FriendUseCases:
    return FriendUseCases(friend_repo)

def get_sos_alert_repository_impl(db: Session = Depends(get_db_session)) -> SOSAlertRepository:
    return SOSAlertRepository()

def get_notification_repository_impl(db: Session = Depends(get_db_session)) -> NotificationRepository:
    return NotificationRepository()

def get_notification_use_cases(
    notification_repo: INotificationRepository = Depends(get_notification_repository_impl)
) -> NotificationUseCases:
    return NotificationUseCases(notification_repo)

def get_admin_log_repository_impl(db: Session = Depends(get_db_session)) -> AdminLogRepository:
    return AdminLogRepository()

def get_admin_log_use_cases(
    admin_log_repo: IAdminLogRepository = Depends(get_admin_log_repository_impl)
) -> AdminLogUseCases:
    return AdminLogUseCases(admin_log_repo)

def get_password_hasher_impl() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()

def get_token_service_impl(
    user_repo_impl: UserRepository = Depends(get_user_repository_impl)
) -> JwtTokenService:
    return JwtTokenService(user_repo_impl)

def provide_user_repository(
    user_repo_impl: UserRepository = Depends(get_user_repository_impl)
) -> IUserRepository:
    return user_repo_impl

def provide_password_hasher(
    hasher_impl: BcryptPasswordHasher = Depends(get_password_hasher_impl)
) -> IPasswordHasher:
    return hasher_impl

def provide_token_service(
    token_service_impl: JwtTokenService = Depends(get_token_service_impl)
) -> ITokenService:
    return token_service_impl

def provide_login_user_use_case(
    user_repo: IUserRepository = Depends(provide_user_repository),
    password_hasher: IPasswordHasher = Depends(provide_password_hasher),
    token_service: ITokenService = Depends(provide_token_service)
) -> LoginUserUseCase:
    return LoginUserUseCase(user_repo, password_hasher, token_service)

def provide_register_user_use_case(
    user_repo: IUserRepository = Depends(provide_user_repository),
    password_hasher: IPasswordHasher = Depends(provide_password_hasher)
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repo, password_hasher)

def provide_logout_user_use_case(
    user_repo: IUserRepository = Depends(provide_user_repository)
) -> LogoutUserUseCase:
    return LogoutUserUseCase(user_repo)

def get_circle_repository_impl(db: Session = Depends(get_db_session)) -> CircleRepository:
    return CircleRepository()

def get_circle_member_repository_impl(db: Session = Depends(get_db_session)) -> CircleMemberRepository:
    return CircleMemberRepository()

from src.application.circle.member_use_cases import CircleMemberUseCases # Import CircleMemberUseCases

def get_circle_use_cases(
    circle_repo: ICircleRepository = Depends(get_circle_repository_impl),
    circle_member_repo: ICircleMemberRepository = Depends(get_circle_member_repository_impl)
) -> CircleUseCases:
    return CircleUseCases(circle_repo, circle_member_repo)

def get_circle_member_use_cases(
    circle_member_repo: ICircleMemberRepository = Depends(get_circle_member_repository_impl)
) -> CircleMemberUseCases:
    return CircleMemberUseCases(circle_member_repo)

def get_sos_alert_use_cases(
    sos_alert_repo: ISOSAlertRepository = Depends(get_sos_alert_repository_impl),
    notification_use_cases: NotificationUseCases = Depends(get_notification_use_cases),
    user_repository: IUserRepository = Depends(provide_user_repository),
    friend_repository: IFriendRepository = Depends(get_friend_repository_impl),
    circle_repository: ICircleRepository = Depends(get_circle_repository_impl),
    circle_member_repository: ICircleMemberRepository = Depends(get_circle_member_repository_impl)
) -> SOSAlertUseCases:
    return SOSAlertUseCases(
        sos_alert_repo,
        notification_use_cases,
        user_repository,
        friend_repository,
        circle_repository,
        circle_member_repository
    )

def get_news_incident_repository_impl(db: Session = Depends(get_db_session)) -> NewsIncidentRepository:
    return NewsIncidentRepository()

def get_news_incident_use_cases(
    repo: INewsIncidentRepository = Depends(get_news_incident_repository_impl)
) -> NewsIncidentUseCases:
    return NewsIncidentUseCases(repo)

def get_user_report_incident_repository_impl(db: Session = Depends(get_db_session)) -> UserReportIncidentRepository:
    return UserReportIncidentRepository()

def get_user_report_incident_use_cases(
    repo: IUserReportIncidentRepository = Depends(get_user_report_incident_repository_impl)
) -> UserReportIncidentUseCases:
    return UserReportIncidentUseCases(repo)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_current_user(
    db: Session = Depends(get_db_session),
    token: str = Depends(oauth2_scheme),
    token_service: ITokenService = Depends(provide_token_service),
    user_repo: IUserRepository = Depends(provide_user_repository)
) -> UserEntity:
    user_id = token_service.verify_token(db, token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user_repo.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_trip_repository_impl(db: Session = Depends(get_db_session)):
    from src.infrastructure.trip.repository_impl import TripRepository
    return TripRepository()

def get_trip_use_cases(
    trip_repo = Depends(get_trip_repository_impl)
):
    from src.application.trip.use_cases import TripUseCases
    return TripUseCases(trip_repo)

def provide_trip_use_cases(
    trip_use_cases: TripUseCases = Depends(get_trip_use_cases)
) -> TripUseCases:
    return trip_use_cases
