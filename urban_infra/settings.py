"""
Django settings for urban_infra project.
Hệ thống Quản lý Hạ tầng Đô thị
"""

from pathlib import Path
import os
from urllib.parse import urlparse

from celery.schedules import crontab
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

def bool_config(name, default=False):
    value = config(name, default=str(default))
    if isinstance(value, bool):
        return value
    value = str(value).strip().lower()
    if value in {'1', 'true', 'yes', 'on', 'dev', 'development'}:
        return True
    if value in {'0', 'false', 'no', 'off', 'prod', 'production', 'release'}:
        return False
    return bool(default)


SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production-!!!')
DEBUG = bool_config('DEBUG', default=True)
ALLOWED_HOSTS = [
    host.strip()
    for host in config('ALLOWED_HOSTS', default='*').split(',')
    if host.strip()
]

DEFAULT_CSRF_TRUSTED_ORIGINS = [
    'https://*.trycloudflare.com',
    'https://urban-infra.duckdns.org',
    'https://urbaninfraqldateam04.us.kg',
    'http://localhost:8000',
]
EXTRA_CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config('CSRF_TRUSTED_ORIGINS', default='').split(',')
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(
    DEFAULT_CSRF_TRUSTED_ORIGINS + EXTRA_CSRF_TRUSTED_ORIGINS
))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'corsheaders',

    # Local apps
    'accounts',
    'infrastructure',
    'maintenance',
    'notifications',
    'inventory',
    'flood',
    'chatbot',
    'hr',
    'maps',
    'contracts',
    'weather',
    'surveys',
    'documents',
    'backup',
    'permits',
    'vehicle_inspection',
    'feedback',
    'integration',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.SessionActivityMiddleware',
]

ROOT_URLCONF = 'urban_infra.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'urban_infra.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'urban_infra.wsgi.application'
ASGI_APPLICATION = 'urban_infra.asgi.application'

DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL:
    parsed_db = urlparse(DATABASE_URL)
    scheme = parsed_db.scheme.lower()
    engine = {
        'postgres': 'django.db.backends.postgresql',
        'postgresql': 'django.db.backends.postgresql',
        'mysql': 'django.db.backends.mysql',
        'sqlite': 'django.db.backends.sqlite3',
    }.get(scheme)

    if engine == 'django.db.backends.sqlite3':
        DATABASES = {
            'default': {
                'ENGINE': engine,
                'NAME': parsed_db.path.lstrip('/') or str(BASE_DIR / 'db.sqlite3'),
            }
        }
    elif engine:
        DATABASES = {
            'default': {
                'ENGINE': engine,
                'NAME': parsed_db.path.lstrip('/'),
                'USER': parsed_db.username or '',
                'PASSWORD': parsed_db.password or '',
                'HOST': parsed_db.hostname or '',
                'PORT': str(parsed_db.port or ''),
            }
        }
    else:
        raise ValueError(f'Unsupported DATABASE_URL scheme: {scheme}')
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Session
SESSION_COOKIE_AGE = 3600  # 1 giờ
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Email
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@urban-infra.vn')

# Redis / Celery
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300
CELERY_BEAT_SCHEDULE = {
    'sync-danang-weather-every-30-minutes': {
        'task': 'weather.tasks.sync_danang_weather',
        'schedule': 30 * 60,
    },
    'notify-expiring-vehicle-inspections-daily': {
        'task': 'vehicle_inspection.tasks.notify_expiring_inspections',
        'schedule': crontab(hour=8, minute=0),
    },
}

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [REDIS_URL]},
    }
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Upload limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800   # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800   # 50MB
ALLOWED_UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.pdf', '.doc', '.docx', '.xls', '.xlsx']

# OTP
OTP_VALIDITY_MINUTES = 5

# System info
SYSTEM_NAME = 'Hệ thống Quản lý Hạ tầng Đô thị'
SYSTEM_SHORT_NAME = 'URBAN INFRA'
SYSTEM_VERSION = '1.0.0'

# Weather API
OPENWEATHER_API_KEY = config('OPENWEATHER_API_KEY', default='')
WEATHER_ALERT_RAIN_MM = config('WEATHER_ALERT_RAIN_MM', default=50, cast=float)

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')
