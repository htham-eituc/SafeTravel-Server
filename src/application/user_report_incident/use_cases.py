from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

from src.domain.user_report_incident.repository_interface import IUserReportIncidentRepository
from src.domain.user_report_incident.entities import UserReportIncident as UserReportIncidentEntity
from src.application.user_report_incident.dto import UserReportIncidentCreate, UserReportIncidentInDB


class UserReportIncidentUseCases:
    def __init__(self, repo: IUserReportIncidentRepository):
        self.repo = repo

    def create_report(
        self,
        db: Session,
        reporter_id: int,
        data: UserReportIncidentCreate
    ) -> UserReportIncidentInDB:
        entity = UserReportIncidentEntity(
            reporter_id=reporter_id,
            title=data.title,
            description=data.description,
            category=data.category,
            latitude=data.latitude,
            longitude=data.longitude,
            severity=data.severity,
            status="active",
            created_at=datetime.utcnow(),
        )
        created = self.repo.create(db, entity)
        return UserReportIncidentInDB.model_validate(created.model_dump())

    def get_reports_within_radius(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float = 0.5
    ) -> List[UserReportIncidentInDB]:
        if radius <= 0:
            raise ValueError("Radius must be greater than 0.")
        incidents = self.repo.get_within_radius(db, latitude, longitude, radius)
        return [UserReportIncidentInDB.model_validate(i.model_dump()) for i in incidents]

