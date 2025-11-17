from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.application.security.security_interfaces import IPasswordHasher, ITokenService
from src.config.settings import get_settings
from src.application.user.dto import TokenData
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.application.security.security_interfaces import IPasswordHasher, ITokenService
from src.config.settings import get_settings
from src.application.user.dto import TokenData
from src.domain.user.repository_interface import IUserRepository
from src.infrastructure.user.repository_impl import UserRepository
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

settings = get_settings()

class BcryptPasswordHasher(IPasswordHasher):
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return self.pwd_context.verify(plain_password, password_hash)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

class JwtTokenService(ITokenService):
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        to_encode.update({"sub": str(data.get("sub"))})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.info(f"Created access token for sub: {data.get('sub')}")
        return encoded_jwt

    def verify_token(self, db: Session, token: str) -> Optional[int]:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id_str: str = payload.get("sub")
            logger.info(f"Token payload 'sub' (user_id_str): {user_id_str}")
            if user_id_str is None:
                logger.warning("Token payload 'sub' is None.")
                raise credentials_exception
            
            try:
                user_id: int = int(user_id_str)
            except ValueError:
                logger.error(f"Could not convert user_id_str '{user_id_str}' to int.")
                raise credentials_exception

            token_data = TokenData(user_id=user_id)
        except JWTError as e:
            logger.error(f"JWTError during token verification: {e}")
            raise credentials_exception
        
        user = self.user_repo.get_user(db, token_data.user_id)
        if user is None:
            logger.warning(f"User with ID {token_data.user_id} not found in repository.")
            raise credentials_exception
        logger.info(f"Token successfully validated for user ID: {user.id}")
        return user.id
