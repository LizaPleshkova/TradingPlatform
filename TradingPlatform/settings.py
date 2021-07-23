"""
Django settings for TradingPlatform project.
"""
import os
from pathlib import Path

from celery import app
from celery.schedules import crontab
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = 'django-insecure-km8!@_)7)%(we8qspi3ku8cc4@q*w8#n3(flu0hf6=(xl&rj&$'
# SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True

# ALLOWED_HOSTS = ['0.0.0.0']
# # ALLOWED_HOSTS = ['*']

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',

    'trading',

    # 'flower',
    'celery',
    # 'django_celery_results',
    # 'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TradingPlatform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
WSGI_APPLICATION = 'TradingPlatform.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'trading_db',
        'NAME': os.getenv("DATABASE_NAME"),
        # 'USER': 'postgres',
        'USER': os.getenv("DATABASE_USER"),
        # 'PASSWORD': 'admin',
        'PASSWORD': os.getenv("DATABASE_PASSWORD"),
        'HOST': 'db',
        'PORT': '5432'
    }
}

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


# AUTH_USER_MODEL = 'trading.UserProfile'

LANGUAGE_CODE = 'ru'


TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# FOR REDIS AND CELERY

# app.conf.beat_schedule = {
#
#     'requirements-every-minutes': {
#         # Регистрируем задачу. Для этого в качестве значения ключа task
#         # Указываем полный путь до созданного нами ранее таска(функции)
#         'task': 'TradingPlatform.tasks.requirements_transaction',
#
#         # Периодичность с которой мы будем запускать нашу задачу
#         # minute='*/5' - говорит о том, что задача должна выполнятся каждые 5 мин.
#         'schedule': crontab(minute='*/1'),
#
#         # Аргументы которые будет принимать функция
#         # 'args': (*args)
#     }
# }

# REDIS_HOST = '0.0.0.0'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 1200}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASKS_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# CELERY_BEAT_SCHEDULE = {}
