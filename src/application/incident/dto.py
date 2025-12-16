from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Union

# DTO for user information associated with an SOS alert
class UserInfoDTO(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None

# DTO for an SOS Alert
class SOSAlertDTO(BaseModel):
    id: int
    user_id: int
    latitude: float
    longitude: float
    message: Optional[str] = None
    created_at: datetime
    user: UserInfoDTO

# DTO for an Incident
class IncidentDTO(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    latitude: float
    longitude: float
    severity: Optional[int] = None
    created_at: datetime

# A union type for the items in the prioritized list
class PrioritizedItem(BaseModel):
    priority: int
    item: Union[SOSAlertDTO, IncidentDTO]

# Request DTO
class GetIncidentsRequestDTO(BaseModel):
    latitude: float
    longitude: float
    radius: float
    user_id: int

# Response DTO

class GetIncidentsResponseDTO(BaseModel):

    items: List[PrioritizedItem]



# DTO for creating an Incident

class IncidentCreateDTO(BaseModel):

    title: str

    description: Optional[str] = None

    category: Optional[str] = None

    latitude: float

    longitude: float

    severity: Optional[int] = None
