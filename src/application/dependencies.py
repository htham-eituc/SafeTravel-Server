from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

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
