from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Annotated
from sqlalchemy.orm import Session
from src.application.dependencies import (
    get_current_user,
    get_db_session,
    get_sos_alert_use_cases, # Changed from provide_sos_alert_use_cases
    get_friend_use_cases, # Changed from provide_friend_use_case
    get_notification_use_cases, # Changed from provide_notification_use_case
    get_circle_use_cases, # Changed from provide_circle_use_cases
    get_news_incident_use_cases,
    get_user_report_incident_use_cases
)
from src.application.sos_alert.dto import (
    SOSAlertCreate,
    SOSAlertUpdate,
    SOSAlertInDB,
    SOSIncidentResponse
)
from src.application.incident.dto import MapIncidentsResponse
from src.application.sos_alert.use_cases import SOSAlertUseCases # Changed from SOSService
from src.application.news_incident.use_cases import NewsIncidentUseCases
from src.application.user_report_incident.use_cases import UserReportIncidentUseCases
from src.application.user_report_incident.dto import UserReportIncidentCreate, UserReportIncidentInDB
from src.application.friend.use_cases import FriendUseCases
from src.application.notification.use_cases import NotificationUseCases
from src.application.notification.dto import NotificationCreate
from src.application.circle.use_cases import CircleUseCases # Added CircleUseCases
from src.domain.user.entities import User as UserEntity
from datetime import datetime

router = APIRouter()

@router.post("/sos", response_model=SOSAlertInDB, status_code=status.HTTP_201_CREATED)
async def send_sos_alert(
    sos_data: SOSAlertCreate,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    sos_alert_use_cases: SOSAlertUseCases = Depends(get_sos_alert_use_cases), # Changed dependency
    circle_use_cases: CircleUseCases = Depends(get_circle_use_cases) # Changed dependency
):
    """
    Send an SOS alert.
    """
    try:
        # Ensure the user_id in sos_data matches the authenticated user
        if sos_data.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to send SOS for another user."
            )
        
        # Get the user's active circle
        active_circles = circle_use_cases.get_circles_by_owner(db, current_user.id)
        active_circle_id = None
        for circle in active_circles:
            if circle.status == "active":
                active_circle_id = circle.id
                break
        
        if active_circle_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not have an active circle to send SOS to."
            )
        
        # Update sos_data with the active circle_id
        sos_data.circle_id = active_circle_id

        new_sos_alert = sos_alert_use_cases.create_sos_alert(db, sos_data) # Changed method call
        return new_sos_alert
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/sos/{alert_id}/status", response_model=SOSAlertInDB)
async def update_sos_alert_status(
    alert_id: int,
    sos_update: SOSAlertUpdate,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    sos_alert_use_cases: SOSAlertUseCases = Depends(get_sos_alert_use_cases), # Changed dependency
    friend_use_case: FriendUseCases = Depends(get_friend_use_cases), # Changed dependency
    notification_use_case: NotificationUseCases = Depends(get_notification_use_cases) # Changed dependency
):
    """
    Update the status of an SOS alert.
    If status is "resolved", notify all friends of the user who sent the SOS.
    """
    try:
        # First, get the existing SOS alert to check ownership
        existing_alert = sos_alert_use_cases.get_sos_alert(db, alert_id) # Changed method call
        if not existing_alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SOS alert not found."
            )
        
        # Ensure the current user is authorized to update this SOS alert
        if existing_alert.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this SOS alert."
            )

        # Update resolved_at if status is changing to "resolved"
        if sos_update.status == "resolved" and existing_alert.status != "resolved":
            sos_update.resolved_at = datetime.now()
        elif sos_update.status != "resolved" and existing_alert.status == "resolved":
            sos_update.resolved_at = None # Clear resolved_at if status changes from resolved

        updated_alert = sos_alert_use_cases.update_sos_alert(db, alert_id, sos_update) # Changed method call
        if not updated_alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SOS alert not found after update attempt."
            )

        # If status is resolved, notify friends
        if updated_alert.status == "resolved":
            friends = friend_use_case.get_friends_by_user_id(db, updated_alert.user_id)
            for friend in friends:
                notification_data = NotificationCreate(
                    user_id=friend.id,
                    title="SOS Alert Resolved",
                    message=f"Your friend {current_user.username}'s SOS alert has been resolved.",
                    type="SOS_RESOLVED",
                    is_read=False
                )
                notification_use_case.create_notification(db, notification_data)

        return updated_alert
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/sos/my_alerts", response_model=List[SOSAlertInDB])
async def get_my_sos_alerts(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    sos_alert_use_cases: SOSAlertUseCases = Depends(get_sos_alert_use_cases) # Changed dependency
):
    """
    Get all SOS alerts for the current authenticated user.
    """
    try:
        alerts = sos_alert_use_cases.get_sos_alerts_by_user(db, current_user.id) # Changed method call
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/sos/incidents", response_model=List[SOSIncidentResponse])
async def get_incident_alerts_for_map(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    latitude: float = Query(..., description="Latitude of the point on the map"),
    longitude: float = Query(..., description="Longitude of the point on the map"),
    radius: float = Query(0.5, gt=0, description="Radius (in degrees) used for proximity search"),
    db: Session = Depends(get_db_session),
    sos_alert_use_cases: SOSAlertUseCases = Depends(get_sos_alert_use_cases)
):
    """
    Get incidents to display on the map. Includes SOS alerts from the user's friends
    or members of active circles the user belongs to, plus alerts within the provided
    radius of the supplied coordinates.
    """
    try:
        incidents = sos_alert_use_cases.get_incidents_for_map(
            db,
            current_user.id,
            latitude,
            longitude,
            radius
        )
        return incidents
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/incidents", response_model=MapIncidentsResponse)
async def get_map_incidents(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    latitude: float = Query(..., description="Latitude of the point on the map"),
    longitude: float = Query(..., description="Longitude of the point on the map"),
    radius: float = Query(0.5, gt=0, description="Radius (in degrees) used for proximity search"),
    db: Session = Depends(get_db_session),
    sos_alert_use_cases: SOSAlertUseCases = Depends(get_sos_alert_use_cases),
    news_incident_use_cases: NewsIncidentUseCases = Depends(get_news_incident_use_cases),
    user_report_incident_use_cases: UserReportIncidentUseCases = Depends(get_user_report_incident_use_cases),
):
    """
    Get map incidents combining:
    - P0: SOS from friends/circles (highest priority)
    - P1: SOS from nearby strangers (radius-based)
    - P2: News-based negative incidents (crime/disaster/etc) stored in DB
    """
    try:
        sos = sos_alert_use_cases.get_incidents_for_map(db, current_user.id, latitude, longitude, radius)
        news = news_incident_use_cases.get_news_incidents_within_radius(db, latitude, longitude, radius)
        reports = user_report_incident_use_cases.get_reports_within_radius(db, latitude, longitude, radius)

        def is_friend_signal(item: SOSIncidentResponse) -> bool:
            friend_sources = {"friend", "circle", "friend_or_circle"}
            return any(source in friend_sources for source in item.sources)

        p0_sos = [item for item in sos if is_friend_signal(item)]
        p1_sos = [item for item in sos if not is_friend_signal(item)]

        return MapIncidentsResponse(
            p0_sos_friends=p0_sos,
            p1_sos_nearby_strangers=p1_sos,
            p1_user_reports=reports,
            p2_news_warnings=news
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")


@router.post("/incidents/report", response_model=UserReportIncidentInDB, status_code=status.HTTP_201_CREATED)
async def report_incident(
    body: UserReportIncidentCreate,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    db: Session = Depends(get_db_session),
    user_report_incident_use_cases: UserReportIncidentUseCases = Depends(get_user_report_incident_use_cases),
):
    """
    User reports an on-map warning (P1).
    """
    try:
        return user_report_incident_use_cases.create_report(db, reporter_id=current_user.id, data=body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
