from typing import List, Set
from sqlalchemy.orm import Session
from src.application.incident.dto import (
    GetIncidentsRequestDTO,
    GetIncidentsResponseDTO,
    PrioritizedItem,
    SOSAlertDTO,
    IncidentDTO,
    UserInfoDTO,
)
from src.domain.incident.repository_interface import IIncidentRepository
from src.domain.sos_alert.repository_interface import ISOSAlertRepository
from src.domain.friend.repository_interface import IFriendRepository
from src.domain.circle.repository_interface import ICircleRepository
from src.domain.circle.member_repository_interface import ICircleMemberRepository
from src.domain.user.repository_interface import IUserRepository


class GetIncidentsUseCase:
    def __init__(
        self,
        incident_repository: IIncidentRepository,
        sos_alert_repository: ISOSAlertRepository,
        friend_repository: IFriendRepository,
        circle_repository: ICircleRepository,
        circle_member_repository: ICircleMemberRepository,
        user_repository: IUserRepository,
    ):
        self.incident_repository = incident_repository
        self.sos_alert_repository = sos_alert_repository
        self.friend_repository = friend_repository
        self.circle_repository = circle_repository
        self.circle_member_repository = circle_member_repository
        self.user_repository = user_repository

    def execute(self, db: Session, request_dto: GetIncidentsRequestDTO) -> GetIncidentsResponseDTO:
        user_id = request_dto.user_id
        latitude = request_dto.latitude
        longitude = request_dto.longitude
        radius = request_dto.radius

        # P0: SOS from friends and circles
        friend_ids = {friend.id for friend in self.friend_repository.get_friends_by_user_id(db, user_id)}
        
        circle_ids = {circle.id for circle in self.circle_repository.get_circles_by_owner(db, user_id)}
        
        member_ids: Set[int] = set()
        for circle_id in circle_ids:
            members = self.circle_member_repository.get_circle_members_by_circle(db, circle_id)
            member_ids.update({member.member_id for member in members})

        related_user_ids = list(friend_ids.union(member_ids))
        
        p0_sos_alerts_entities = self.sos_alert_repository.get_sos_alerts_by_user_ids(db, related_user_ids) if related_user_ids else []
        
        p0_items: List[PrioritizedItem] = []
        for alert in p0_sos_alerts_entities:
            user_entity = self.user_repository.get_user_by_id(db, alert.user_id)
            user_dto = UserInfoDTO.model_validate(user_entity.__dict__) if user_entity else None
            if user_dto:
                p0_items.append(
                    PrioritizedItem(
                        priority=0,
                        item=SOSAlertDTO(
                            **alert.model_dump(),
                            user=user_dto
                        )
                    )
                )

        p0_alert_ids = {alert.id for alert in p0_sos_alerts_entities}

        # P1: SOS from nearby users
        p1_sos_alerts_entities = self.sos_alert_repository.get_sos_alerts_within_radius(
            db, latitude, longitude, radius
        )
        
        p1_items: List[PrioritizedItem] = []
        for alert in p1_sos_alerts_entities:
            if alert.id not in p0_alert_ids:
                user_entity = self.user_repository.get_user_by_id(db, alert.user_id)
                user_dto = UserInfoDTO.model_validate(user_entity.__dict__) if user_entity else None
                if user_dto:
                    p1_items.append(
                        PrioritizedItem(
                            priority=1,
                            item=SOSAlertDTO(
                                **alert.model_dump(),
                                user=user_dto
                            )
                        )
                    )

        # P2: Incidents from reports
        p2_incident_entities = self.incident_repository.get_within_radius(
            db, latitude, longitude, radius
        )
        p2_items: List[PrioritizedItem] = [
            PrioritizedItem(priority=2, item=IncidentDTO.model_validate(incident.__dict__))
            for incident in p2_incident_entities
        ]

        # Combine and sort
        all_items = p0_items + p1_items + p2_items
        all_items.sort(key=lambda x: (x.priority, x.item.created_at if hasattr(x.item, 'created_at') else datetime.min), reverse=True)

        return GetIncidentsResponseDTO(items=all_items)


from src.application.incident.dto import IncidentCreateDTO
from src.domain.incident.entities import Incident as IncidentEntity
from datetime import datetime

class CreateIncidentUseCase:
    def __init__(self, incident_repository: IIncidentRepository):
        self.incident_repository = incident_repository

    def execute(self, db: Session, incident_create_dto: IncidentCreateDTO) -> IncidentDTO:
        incident_entity = IncidentEntity(
            **incident_create_dto.model_dump(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        created_incident = self.incident_repository.create(db, incident_entity)
        return IncidentDTO.model_validate(created_incident.__dict__)
