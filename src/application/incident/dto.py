from pydantic import BaseModel
from typing import List

from src.application.sos_alert.dto import SOSIncidentResponse


class MapIncidentsResponse(BaseModel):
    p0_sos_friends: List[SOSIncidentResponse]
    p1_sos_nearby_strangers: List[SOSIncidentResponse]
