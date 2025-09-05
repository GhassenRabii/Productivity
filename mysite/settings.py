import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (from deploy.sh -> .env)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key and debug
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'changeme-in-production')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

# Static and media
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Allowed hosts
ALLOWED_HOSTS = [
    'django-albv2-2097968036.eu-central-1.elb.amazonaws.com',
    'productivity.dunedivision.com',
    'localhost',
    '127.0.0.1',
    '10.10.102.83'
]

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    "https://django-albv2-1620044498.eu-central-1.elb.amazonaws.com",
    "https://productivity.dunedivision.com"
]

# Security for production/HTTPS
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_HSTS_SECONDS = 0  
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_SSL_REDIRECT = False
else:
    SECURE_SSL_REDIRECT = False

# Application definition
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tasks',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'mozilla_django_oidc'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS config
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://productivity.dunedivision.com",
]
CORS_ALLOW_CREDENTIALS = True

# Swagger (drf-yasg)
SWAGGER_SETTINGS = {
    "DEFAULT_API_URL": "https://productivity.dunedivision.com",
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    },
}

# DRF defaults
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# Auth / login
LOGIN_URL = '/oidc/authenticate/'        # changed to OIDC
LOGIN_REDIRECT_URL = '/tasks/'
LOGOUT_REDIRECT_URL = '/'

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# Database (Postgres)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'productivitydb'),
        'USER': os.environ.get('DB_USER', 'dbadmin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'tasks': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

# -----------------------------------------------------------------
# Cognito OIDC integration
# -----------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # keep default
    "tasks.auth.MyOIDCBackend",                   # custom OIDC backend
]

# Values from CloudFormation outputs (deploy.sh should write these to .env)
AWS_REGION = os.environ.get("AWS_REGION", "eu-central-1")
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_CLIENT_SECRET = os.environ.get("COGNITO_CLIENT_SECRET")
COGNITO_DOMAIN_PREFIX = os.environ.get("COGNITO_DOMAIN_PREFIX")  # e.g. myapp-prod

OIDC_OP_DISCOVERY_ENDPOINT = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/openid-configuration"
OIDC_RP_CLIENT_ID = COGNITO_CLIENT_ID
OIDC_RP_CLIENT_SECRET = COGNITO_CLIENT_SECRET
OIDC_RP_SCOPES = "openid email phone profile"
OIDC_STORE_ID_TOKEN = True
OIDC_STORE_ACCESS_TOKEN = True

# Hosted UI logout endpoint
if COGNITO_DOMAIN_PREFIX:
    OIDC_OP_LOGOUT_ENDPOINT = f"https://{COGNITO_DOMAIN_PREFIX}.auth.{AWS_REGION}.amazoncognito.com/logout"
