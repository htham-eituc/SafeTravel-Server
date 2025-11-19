# Import all models here to ensure they are registered with SQLAlchemy's metadata
from .user import models
from .circle import models as circle_models
from .circle import member_models
from .location import models as location_models
from .notification import models as notification_models
from .admin_log import models as admin_log_models
from .friend import models as friend_models
from .sos_alert import models as sos_alert_models # Added missing import for SOSAlert
# Add other model imports as needed
