from celery import Celery
from paths import SERVICE_NAME  # Reuse existing config

# Configure Celery app
app = Celery(
    SERVICE_NAME,
    broker="redis://localhost:6379/0",  # Or use env var for flexibility
    backend="redis://localhost:6379/0",
    include=["app.tasks"]  # Where training tasks will be defined
)

# Optional: Auto-discover tasks
app.autodiscover_tasks()