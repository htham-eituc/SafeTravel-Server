from typing import List
from sqlalchemy.orm import Session

from src.domain.user_report_incident.entities import UserReportIncident as UserReportIncidentEntity
from src.domain.user_report_incident.repository_interface import IUserReportIncidentRepository
from src.infrastructure.user_report_incident.models import UserReportIncident


class UserReportIncidentRepository(IUserReportIncidentRepository):
    def create(self, db: Session, incident: UserReportIncidentEntity) -> UserReportIncidentEntity:
        db_incident = UserReportIncident(
            reporter_id=incident.reporter_id,
            title=incident.title,
            description=incident.description,
            category=incident.category,
            latitude=incident.latitude,
            longitude=incident.longitude,
            severity=incident.severity,
            status=incident.status,
        )
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)
        return UserReportIncidentEntity.model_validate(db_incident.__dict__)

    def get_within_radius(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float
    ) -> List[UserReportIncidentEntity]:
        lat_min = latitude - radius
        lat_max = latitude + radius
        lon_min = longitude - radius
        lon_max = longitude + radius

        incidents = db.query(UserReportIncident).filter(
            UserReportIncident.status == "active",
            UserReportIncident.latitude.between(lat_min, lat_max),
            UserReportIncident.longitude.between(lon_min, lon_max),
        ).all()
        return [UserReportIncidentEntity.model_validate(i.__dict__) for i in incidents]

