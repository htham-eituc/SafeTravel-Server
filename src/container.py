from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from src.application.security.security_interfaces import IPasswordHasher, ITokenService
from src.application.user.auth_use_cases import (
    LoginUserUseCase,
    RegisterUserUseCase,
    LogoutUserUseCase
)
from src.domain.user.repository_interface import UserRepositoryInterface
from src.infrastructure.database.sql.database import get_db
from src.infrastructure.security.security_impl import BcryptPasswordHasher, JwtTokenService
from src.infrastructure.user.repository_impl import UserRepositoryImpl
from src.application.user.dto import TokenData 

def get_db_session() -> Session:
    yield from get_db()

def get_user_repository_impl(db: Session = Depends(get_db_session)) -> UserRepositoryImpl:
    return UserRepositoryImpl(db)

def get_password_hasher_impl() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()

def get_token_service_impl(
    user_repo_impl: UserRepositoryImpl = Depends(get_user_repository_impl)
) -> JwtTokenService:
    return JwtTokenService(user_repo_impl)

def provide_user_repository(
    user_repo_impl: UserRepositoryImpl = Depends(get_user_repository_impl)
) -> UserRepositoryInterface:
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
    user_repo: UserRepositoryInterface = Depends(provide_user_repository),
    password_hasher: IPasswordHasher = Depends(provide_password_hasher),
    token_service: ITokenService = Depends(provide_token_service)
) -> LoginUserUseCase:
    return LoginUserUseCase(user_repo, password_hasher, token_service)

def provide_register_user_use_case(
    user_repo: UserRepositoryInterface = Depends(provide_user_repository),
    password_hasher: IPasswordHasher = Depends(provide_password_hasher)
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repo, password_hasher)

def provide_logout_user_use_case(
    user_repo: UserRepositoryInterface = Depends(provide_user_repository)
) -> LogoutUserUseCase:
    return LogoutUserUseCase(user_repo)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login") # Changed tokenUrl to the full path

async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    token_service: ITokenService = Depends(provide_token_service)
) -> int:
    user_id = token_service.verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
