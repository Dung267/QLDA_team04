from .base import *

DEBUG = False

ALLOWED_HOSTS = ["yourdomain.com", "sub.yourdomain.com"]

DATABASES["default"].update({
    "HOST": "your-db-host",
    "PORT": "3306",
})

CELERY_BROKER_URL = "redis://your-redis-host:6379/0"
CELERY_RESULT_BACKEND = "redis://your-redis-host:6379/0"

# Bảo mật và thiết lập môi trường email sản xuất
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.your-email-service.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "no-reply@yourdomain.com"