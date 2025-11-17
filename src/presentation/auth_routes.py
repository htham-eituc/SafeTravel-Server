from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session # Thêm import Session

from src.application.user.auth_use_cases import (
    LoginUserUseCase,
    RegisterUserUseCase,
    LogoutUserUseCase
)
from src.application.user.dto import UserLoginDTO, UserRegisterDTO, AuthTokenDTO, UserDTO
from src.container import ( 
    provide_login_user_use_case,
    provide_register_user_use_case,
    provide_logout_user_use_case,
    get_current_user_id,
    get_db_session
)

router = APIRouter()


@router.post("/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterDTO,
    db: Session = Depends(get_db_session),
    register_use_case: RegisterUserUseCase = Depends(provide_register_user_use_case)
):
    try:
        new_user = register_use_case.execute(db, user_data)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



@router.post("/login", response_model=AuthTokenDTO)

async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db_session),
    login_use_case: LoginUserUseCase = Depends(provide_login_user_use_case)
):
    user_login_dto = UserLoginDTO(email=form_data.username, password=form_data.password)
    try:
        token = login_use_case.execute(db, user_login_dto)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db_session),
    logout_use_case: LogoutUserUseCase = Depends(provide_logout_user_use_case)
):
    logout_use_case.execute(db, current_user_id)
    return {"message": "Successfully logged out"}
