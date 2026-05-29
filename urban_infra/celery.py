import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "urban_infra.settings")

app = Celery("urban_infra")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

