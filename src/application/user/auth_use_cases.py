from sqlalchemy.orm import Session # Thêm import Session
from src.domain.user.repository_interface import IUserRepository
from src.domain.user.entities import User
from src.application.user.dto import UserLoginDTO, UserRegisterDTO, UserDTO, AuthTokenDTO
from src.application.security.security_interfaces import IPasswordHasher, ITokenService
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class LoginUserUseCase:
    def __init__(self, user_repo: IUserRepository, password_hasher: IPasswordHasher, token_service: ITokenService):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.token_service = token_service

    def execute(self, db: Session, login_dto: UserLoginDTO) -> AuthTokenDTO:
        logger.info(f"Attempting to log in user with email: {login_dto.email}")
        user = self.user_repo.get_user_by_email(db, email=login_dto.email)
        if not user:
            logger.warning(f"Login failed for email: {login_dto.email} - User not found")
            raise ValueError("Invalid credentials")
        
        logger.debug(f"Login attempt for {login_dto.email}. Provided password: {login_dto.password}, Stored hash: {user.hashed_password}") # Debug log
        if not self.password_hasher.verify_password(login_dto.password, user.hashed_password):
            logger.warning(f"Login failed for email: {login_dto.email} - Password mismatch")
            raise ValueError("Invalid credentials")
        
        access_token = self.token_service.create_access_token(data={"sub": user.id})
        logger.info(f"User {user.email} logged in successfully.")
        return AuthTokenDTO(access_token=access_token, token_type="bearer")

class RegisterUserUseCase:
    def __init__(self, user_repo: IUserRepository, password_hasher: IPasswordHasher):
        self.user_repo = user_repo
        self.password_hasher = password_hasher

    def execute(self, db: Session, register_dto: UserRegisterDTO) -> UserDTO:
        logger.info(f"Attempting to register new user with email: {register_dto.email}")
        existing_user = self.user_repo.get_user_by_email(db, email=register_dto.email)
        if existing_user:
            logger.warning(f"Registration failed for email: {register_dto.email} - Email already registered")
            raise ValueError("Email already registered")
        
        password_hash = self.password_hasher.get_password_hash(register_dto.password)
        logger.debug(f"Generated password hash for {register_dto.email}: {password_hash}") # Debug log
        new_user = User(
            username=register_dto.name,
            email=register_dto.email,
            phone=register_dto.phone,
            avatar_url=register_dto.avatar_url,
            hashed_password=password_hash,
            full_name=register_dto.name, # Assuming full_name is the same as name for registration
            disabled=False # Default value
        )
        created_user = self.user_repo.create_user(db, user_data=new_user)
        logger.info(f"User {created_user.email} registered successfully with ID: {created_user.id}")
        return UserDTO(
            id=created_user.id,
            name=created_user.username,
            email=created_user.email,
            phone=created_user.phone,
            avatar_url=created_user.avatar_url,
            full_name=created_user.full_name, # Ánh xạ full_name vào UserDTO
            created_at=created_user.created_at
        )

class LogoutUserUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def execute(self, db: Session, user_id: int):
        logger.info(f"Attempting to log out user with ID: {user_id}")
        user = self.user_repo.get_user(db, user_id=user_id)
        if user:
            logger.info(f"User {user.email} (ID: {user_id}) logged out successfully.")
        else:
            logger.warning(f"Logout attempted for non-existent user ID: {user_id}")
        pass
