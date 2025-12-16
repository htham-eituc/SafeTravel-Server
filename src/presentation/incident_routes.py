from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated
from sqlalchemy.orm import Session

from src.application.dependencies import get_current_user, get_db_session, get_incidents_use_cases
from src.application.incident.dto import GetIncidentsRequestDTO, GetIncidentsResponseDTO
from src.application.incident.use_cases import GetIncidentsUseCase
from src.domain.user.entities import User as UserEntity
import logging
import traceback
from src.application.dependencies import get_delete_incident_use_case
from src.application.incident.use_cases import DeleteIncidentUseCase
from src.application.dependencies import get_create_incident_use_case
from src.application.incident.dto import IncidentCreateDTO, IncidentDTO
from src.application.incident.use_cases import CreateIncidentUseCase
    
router = APIRouter()


@router.get("/incidents", response_model=GetIncidentsResponseDTO)
async def get_incidents(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius: float = Query(..., gt=0),
    db: Session = Depends(get_db_session),
    use_cases: GetIncidentsUseCase = Depends(get_incidents_use_cases),
):
    """
    Get prioritized incidents and SOS alerts.
    - P0: SOS from friends and circles
    - P1: SOS from nearby users
    - P2: Incidents from reports
    """
    try:
        request_dto = GetIncidentsRequestDTO(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            user_id=current_user.id
        )
        return use_cases.execute(db, request_dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging.exception("Error in get_incidents")
        # include traceback in server logs and return a short message to client
        tb = traceback.format_exc()
        logging.error(tb)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: int,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    use_case: DeleteIncidentUseCase = Depends(get_delete_incident_use_case),
):
    """
    Delete an incident by ID.
    """
    try:
        deleted = use_case.execute(db, incident_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    except HTTPException:
        raise
    except Exception:
        logging.exception("Error deleting incident")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")




@router.post("/incidents", response_model=IncidentDTO, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: IncidentCreateDTO,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    use_case: CreateIncidentUseCase = Depends(get_create_incident_use_case),
):
    """
    Create a new incident report.
    """
    try:
        return use_case.execute(db, incident_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
