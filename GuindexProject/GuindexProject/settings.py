"""
Django settings for GuindexProject project.
"""

import os

import GuindexProject.guin_secrets as secrets

PROJECT_TITLE = "Guindex"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = secrets.KEY

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")

USE_TZ = True

# Behind nginx/terminating TLS: trust X-Forwarded-Proto for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # Set True only after you understand HSTS preload (irreversible for users)
    SECURE_HSTS_PRELOAD = os.environ.get("SECURE_HSTS_PRELOAD", "").lower() in (
        "1",
        "true",
        "yes",
    )

ALLOWED_HOSTS = [
    "45.79.148.4",
    "guindex.ie",
    "www.guindex.ie",
    "127.0.0.1",
    "172.28.5.22",
    "172.28.4.152",
    "10.0.3.148",
]

# Required for HTTPS POSTs (login, forms) when behind nginx; scheme + host (+ :port if non-default).
# Not read from env by default — add origins here or extend via DJANGO_CSRF_TRUSTED_ORIGINS below.
CSRF_TRUSTED_ORIGINS = [
    "https://guindex.ie",
    "https://www.guindex.ie",
]
_extra_csrf = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").strip()
if _extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend(
        o.strip() for o in _extra_csrf.split(",") if o.strip()
    )
    CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_extensions",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_datatables",
    "drf_spectacular",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "UserProfile",
    "Guindex",
    "GuindexWebClient",
    "TelegramUser",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# Default is DENY, which blocks map.html's same-origin iframe to /guindex_map.
# SAMEORIGIN still prevents other sites embedding your pages (clickjacking).
X_FRAME_OPTIONS = "SAMEORIGIN"

# OSM tile servers require a non-empty Referer (tile usage policy). Sending the
# page origin on cross-origin requests (e.g. map tiles) satisfies this.
SECURE_REFERRER_POLICY = "origin-when-cross-origin"

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "GuindexProject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "GuindexProject.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": secrets.GUINDEX_DB_LOCATION,
    }
}

# Throttling (and anything using caches) needs a working backend.
# Database cache: run once after migrate: python manage.py createcachetable
# Or set DJANGO_CACHE_BACKEND=locmem for dev / single Gunicorn worker (no extra table).
_cache_backend = os.environ.get("DJANGO_CACHE_BACKEND", "database").strip().lower()
if _cache_backend == "locmem":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "guindex_cache",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "CDN/")

EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = secrets.EMAIL
EMAIL_HOST_PASSWORD = secrets.PASSWORD
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "/"

LOG_DIR = os.environ.get("GUINDEX_LOG_DIR", os.path.join(BASE_DIR, "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "TelegramUserLogFile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "TelegramUser.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "verbose",
        },
        "GuindexLogFile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "Guindex.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "verbose",
        },
        "GuindexWebClientLogFile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "GuindexWebClient.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "verbose",
        },
        "GuindexStatsLogFile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "GuindexStats.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "verbose",
        },
        "GuindexAlertsLogFile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "GuindexAlerts.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "verbose",
        },
        "GuindexDbBackupLogFile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "GuindexDbBackup.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "verbose",
        },
        "GuindexBotLogFile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "GuindexBot.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "verbose",
        },
        "GuindexMapLogFile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "GuindexMap.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "TelegramUser": {
            "handlers": ["TelegramUserLogFile"],
            "propagate": True,
            "level": "DEBUG",
        },
        "Guindex": {
            "handlers": ["GuindexLogFile"],
            "propagate": True,
            "level": "DEBUG",
        },
        "GuindexWebClient": {
            "handlers": ["GuindexWebClientLogFile"],
            "propagate": True,
            "level": "DEBUG",
        },
        "GuindexStats": {
            "handlers": ["GuindexStatsLogFile"],
            "propagate": True,
            "level": "DEBUG",
        },
        "GuindexAlerts": {
            "handlers": ["GuindexAlertsLogFile"],
            "propagate": True,
            "level": "DEBUG",
        },
        "GuindexDbBackup": {
            "handlers": ["GuindexDbBackupLogFile"],
            "propagate": True,
            "level": "DEBUG",
        },
        "GuindexBot": {
            "handlers": ["GuindexBotLogFile"],
            "propagate": True,
            "level": "DEBUG",
        },
        "GuindexMap": {
            "handlers": ["GuindexMapLogFile"],
            "propagate": True,
            "level": "DEBUG",
        },
    },
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework_datatables.renderers.DatatablesRenderer",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_datatables.filters.DatatablesFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework_datatables.pagination.DatatablesPageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10000/day",
        "user": "10000/day",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Guindex HTTP API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

BOT_HTTP_API_TOKEN = secrets.BOT_HTTP_API_TOKEN

GOOGLE_MAPS_API_KEY = secrets.GOOGLE_MAPS_API_KEY

DROPBOX_API_KEY = secrets.DROPBOX_API_KEY
DROPBOX_API_SECRET = secrets.DROPBOX_API_SECRET
DROPBOX_API_ACCESS_TOKEN = secrets.DROPBOX_API_ACCESS_TOKEN

FACEBOOK_APP_ID = secrets.FACEBOOK_APP_ID

GOOGLE_ANALYTICS_KEY = secrets.GOOGLE_ANALYTICS_KEY

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

GOOGLE_AUTH_CLIENT_ID = secrets.GOOGLE_AUTH_CLIENT_ID

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

REST_AUTH = {
    "TOKEN_SERIALIZER": "UserProfile.serializers.TokenSerializer",
}
