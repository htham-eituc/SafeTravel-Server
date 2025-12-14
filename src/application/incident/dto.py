from pydantic import BaseModel
from typing import List

from src.application.sos_alert.dto import SOSIncidentResponse
from src.application.news_incident.dto import NewsIncidentInDB
from src.application.user_report_incident.dto import UserReportIncidentInDB


class MapIncidentsResponse(BaseModel):
    p0_sos_friends: List[SOSIncidentResponse]
    p1_sos_nearby_strangers: List[SOSIncidentResponse]
    p1_user_reports: List[UserReportIncidentInDB]
    p2_news_warnings: List[NewsIncidentInDB]
