from typing import List
import hashlib
from sqlalchemy.orm import Session

from src.domain.news_incident.entities import NewsIncident as NewsIncidentEntity
from src.domain.news_incident.repository_interface import INewsIncidentRepository
from src.infrastructure.news_incident.models import NewsIncident


class NewsIncidentRepository(INewsIncidentRepository):
    def upsert_by_source_url(self, db: Session, incident: NewsIncidentEntity) -> NewsIncidentEntity:
        source_url_hash = hashlib.sha256(incident.source_url.encode("utf-8")).hexdigest()
        existing = db.query(NewsIncident).filter(NewsIncident.source_url_hash == source_url_hash).first()
        if existing:
            for key, value in incident.model_dump(exclude_unset=True).items():
                if key in {"id", "created_at", "updated_at"}:
                    continue
                setattr(existing, key, value)
            existing.source_url_hash = source_url_hash
            db.commit()
            db.refresh(existing)
            return NewsIncidentEntity.model_validate(existing.__dict__)

        db_incident = NewsIncident(
            title=incident.title,
            summary=incident.summary,
            category=incident.category,
            location_name=incident.location_name,
            latitude=incident.latitude,
            longitude=incident.longitude,
            source_url=incident.source_url,
            source_url_hash=source_url_hash,
            published_at=incident.published_at,
            severity=incident.severity,
        )
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)
        return NewsIncidentEntity.model_validate(db_incident.__dict__)

    def get_within_radius(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float
    ) -> List[NewsIncidentEntity]:
        lat_min = latitude - radius
        lat_max = latitude + radius
        lon_min = longitude - radius
        lon_max = longitude + radius

        incidents = db.query(NewsIncident).filter(
            NewsIncident.latitude.between(lat_min, lat_max),
            NewsIncident.longitude.between(lon_min, lon_max)
        ).all()
        return [NewsIncidentEntity.model_validate(i.__dict__) for i in incidents]
