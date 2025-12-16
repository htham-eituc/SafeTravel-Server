from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated, List
from sqlalchemy.orm import Session

from src.application.dependencies import get_current_user, get_db_session, get_news_incident_use_cases
from src.application.news_incident.dto import NewsIncidentExtractRequest, NewsIncidentInDB
from src.application.news_incident.use_cases import NewsIncidentUseCases
from src.domain.user.entities import User as UserEntity


router = APIRouter()


@router.post("/news-incidents/extract", response_model=List[NewsIncidentInDB], status_code=status.HTTP_201_CREATED)
async def extract_news_incidents(
    body: NewsIncidentExtractRequest,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    use_cases: NewsIncidentUseCases = Depends(get_news_incident_use_cases),
):
    """
    Extract negative incidents from news sources (AI + search), geocode to lat/long, and store them.
    Requires GEOAPIFY_KEY and GEMINI_API_KEY configured on the server.
    """
    try:
        return use_cases.extract_and_store(db, query=body.query, days=body.days, max_items=body.max_items)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/news-incidents", response_model=List[NewsIncidentInDB])
async def get_news_incidents(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius: float = Query(0.5, gt=0),
    db: Session = Depends(get_db_session),
    use_cases: NewsIncidentUseCases = Depends(get_news_incident_use_cases),
):
    try:
        return use_cases.get_news_incidents_within_radius(db, latitude=latitude, longitude=longitude, radius=radius)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
