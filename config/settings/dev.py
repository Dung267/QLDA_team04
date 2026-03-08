from .base import *

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "localhost:8000"]

DATABASES["default"].update({
    "HOST": "127.0.0.1",
    "PORT": "3306",
})

CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # Thư email console trong dev