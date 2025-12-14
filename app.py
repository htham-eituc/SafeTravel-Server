"""
Compatibility entrypoint for ASGI servers.

Some deployments (or IDE templates) expect the application to be available as `app:app`.
The canonical app lives in `run.py`.
"""

from run import app

