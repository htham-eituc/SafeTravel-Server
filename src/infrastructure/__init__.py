# Import all models here to ensure they are registered with SQLAlchemy's metadata
from .user import models
from .circle import models as circle_models
from .circle import member_models
from .location import models as location_models
from .notification import models as notification_models
from .admin_log import models as admin_log_models
from .friend import models as friend_models
from .sos_alert import models as sos_alert_models # Added missing import for SOSAlert
from .trip import models as trip_models
from .news_incident import models as news_incident_models
from .user_report_incident import models as user_report_incident_models

# Add other model imports as needed
