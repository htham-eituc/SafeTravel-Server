from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.application.admin_log.dto import AdminLogCreate, AdminLogUpdate, AdminLogInDB
from src.application.admin_log.use_cases import AdminLogUseCases
from src.infrastructure.admin_log.repository_impl import AdminLogRepository
from src.infrastructure.database.sql.database import get_db
from src.application.dependencies import get_admin_log_use_cases

router = APIRouter()

@router.post("/admin_logs", response_model=AdminLogInDB, status_code=status.HTTP_201_CREATED)
def create_admin_log_route(
    admin_log_data: AdminLogCreate,
    admin_log_use_cases: AdminLogUseCases = Depends(get_admin_log_use_cases),
    db: Session = Depends(get_db)
):
    admin_log = admin_log_use_cases.create_admin_log(db, admin_log_data)
    return AdminLogInDB.model_validate(admin_log)

@router.get("/admin_logs/{admin_log_id}", response_model=AdminLogInDB)
def get_admin_log_route(
    admin_log_id: int,
    admin_log_use_cases: AdminLogUseCases = Depends(get_admin_log_use_cases),
    db: Session = Depends(get_db)
):
    admin_log = admin_log_use_cases.get_admin_log(db, admin_log_id)
    if not admin_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin log not found")
    return AdminLogInDB.model_validate(admin_log)

@router.get("/admins/{admin_id}/admin_logs", response_model=List[AdminLogInDB])
def get_admin_logs_by_admin_route(
    admin_id: int,
    admin_log_use_cases: AdminLogUseCases = Depends(get_admin_log_use_cases),
    db: Session = Depends(get_db)
):
    admin_logs = admin_log_use_cases.get_admin_logs_by_admin(db, admin_id)
    return [AdminLogInDB.model_validate(log) for log in admin_logs]

@router.put("/admin_logs/{admin_log_id}", response_model=AdminLogInDB)
def update_admin_log_route(
    admin_log_id: int,
    admin_log_update: AdminLogUpdate,
    admin_log_use_cases: AdminLogUseCases = Depends(get_admin_log_use_cases),
    db: Session = Depends(get_db)
):
    admin_log = admin_log_use_cases.update_admin_log(db, admin_log_id, admin_log_update)
    if not admin_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin log not found")
    return AdminLogInDB.model_validate(admin_log)

@router.delete("/admin_logs/{admin_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_log_route(
    admin_log_id: int,
    admin_log_use_cases: AdminLogUseCases = Depends(get_admin_log_use_cases),
    db: Session = Depends(get_db)
):
    if not admin_log_use_cases.delete_admin_log(db, admin_log_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin log not found")
    return
