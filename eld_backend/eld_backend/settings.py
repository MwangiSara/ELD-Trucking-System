from pathlib import Path
import os
from decouple import config
from datetime import timedelta
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default = 'True')

ALLOWED_HOSTS =  ['localhost', '127.0.0.1', "eld-trucking-system.onrender.com"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party apps
    'rest_framework',
    'corsheaders',

    # local apps
    'trips',


]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eld_backend.urls'

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

WSGI_APPLICATION = 'eld_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# for development
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('MAIN_DB'),
#         'PORT': config('MAIN_DB_PORT'),
#         'PASSWORD': config('MAIN_DB_USER_PASSWORD'),
#         'USER': config('MAIN_DB_USER'),
#         'HOST': config('MAIN_DB_HOST',  default='5432'),
#     }
# }

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    "FORMAT_SUFFIX_KWARG": "format",
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        "rest_framework.parsers.MultiPartParser",
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
}


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173", # for development
    "http://127.0.0.1:5173",
    "https://eld-trucking-system.vercel.app"
]

CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_ALL_ORIGINS = DEBUG  # for development

# ELD specific settings
ELD_SETTINGS = {
    'MAX_DRIVING_HOURS_PER_DAY': 11,
    'MAX_ON_DUTY_HOURS_PER_DAY': 14,
    'REQUIRED_REST_PERIOD_HOURS': 10,
    'MAX_CYCLE_HOURS_70_8': 70,  # 70 hrs/8 days
    'MAX_CYCLE_HOURS_60_7': 60,  # 60 hrs/7 days
    'MANDATORY_BREAK_AFTER_HOURS': 8,  # 30-min/ 8 hrs
    'MANDATORY_BREAK_DURATION': 0.5,  # 30 minutes
    'FUEL_STOP_INTERVAL_MILES': 1000,  # Average fuel stop interval
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/eld_tracker.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'eld_tracker': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Create logs dir 
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
