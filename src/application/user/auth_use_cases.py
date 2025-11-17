from src.domain.user.repository_interface import UserRepositoryInterface
from src.domain.user.entities import User
from src.application.user.dto import UserLoginDTO, UserRegisterDTO, UserDTO, AuthTokenDTO
from src.application.security.security_interfaces import IPasswordHasher, ITokenService # New import
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class LoginUserUseCase:
    def __init__(self, user_repo: UserRepositoryInterface, password_hasher: IPasswordHasher, token_service: ITokenService):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.token_service = token_service

    def execute(self, login_dto: UserLoginDTO) -> AuthTokenDTO:
        logger.info(f"Attempting to log in user with email: {login_dto.email}")
        user = self.user_repo.get_by_email(login_dto.email)
        if not user or not self.password_hasher.verify_password(login_dto.password, user.password_hash):
            logger.warning(f"Login failed for email: {login_dto.email} - Invalid credentials")
            raise ValueError("Invalid credentials")
        
        access_token = self.token_service.create_access_token(data={"sub": user.id}) # Use token_service
        logger.info(f"User {user.email} logged in successfully.")
        return AuthTokenDTO(access_token=access_token, token_type="bearer")

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepositoryInterface, password_hasher: IPasswordHasher):
        self.user_repo = user_repo
        self.password_hasher = password_hasher

    def execute(self, register_dto: UserRegisterDTO) -> UserDTO:
        logger.info(f"Attempting to register new user with email: {register_dto.email}")
        existing_user = self.user_repo.get_by_email(register_dto.email)
        if existing_user:
            logger.warning(f"Registration failed for email: {register_dto.email} - Email already registered")
            raise ValueError("Email already registered")
        
        password_hash = self.password_hasher.get_password_hash(register_dto.password) # Use password_hasher
        new_user = User(
            name=register_dto.name,
            email=register_dto.email,
            password_hash=password_hash,
            phone=register_dto.phone,
            avatar_url=register_dto.avatar_url
        )
        created_user = self.user_repo.create(new_user)
        logger.info(f"User {created_user.email} registered successfully with ID: {created_user.id}")
        return UserDTO(
            id=created_user.id,
            name=created_user.name,
            email=created_user.email,
            phone=created_user.phone,
            avatar_url=created_user.avatar_url,
            created_at=created_user.created_at
        )

class LogoutUserUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    def execute(self, user_id: int): # Changed to int
        logger.info(f"Attempting to log out user with ID: {user_id}")
        # For JWT, logout is typically handled client-side by discarding the token.
        # If server-side token invalidation (e.g., blacklist) is needed, implement it here.
        # For now, we just log the action.
        user = self.user_repo.get_by_id(user_id) # user_id is int
        if user:
            logger.info(f"User {user.email} (ID: {user_id}) logged out successfully.")
        else:
            logger.warning(f"Logout attempted for non-existent user ID: {user_id}")
        pass
