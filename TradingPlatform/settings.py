"""
Django settings for TradingPlatform project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = 'django-insecure-km8!@_)7)%(we8qspi3ku8cc4@q*w8#n3(flu0hf6=(xl&rj&$'
# SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0']
# ALLOWED_HOSTS = ['*']
# Application definition
# == == == =
# # SECURITY WARNING: keep the secret key used in production secret!
# # SECRET_KEY = 'django-insecure-km8!@_)7)%(we8qspi3ku8cc4@q*w8#n3(flu0hf6=(xl&rj&$'
# SECRET_KEY = os.getenv("SECRET_KEY")
#
# DEBUG = True
#
# ALLOWED_HOSTS = []
# >> >> >> > develop

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

        'NAME': 'trading_db',
        'NAME': os.getenv("DATABASE_NAME"),
        'USER': 'postgres',
        'USER': os.getenv("DATABASE_USER"),
        'PASSWORD': 'admin',
        'PASSWORD': os.getenv("DATABASE_PASSWORD"),
        'HOST': 'db',
        # =======
        #         # 'NAME': 'trading_db',
        #         'NAME': os.getenv("DATABASE_NAME"),
        #         # 'USER': 'admin',
        #         'USER': os.getenv("DATABASE_USER"),
        #         # 'PASSWORD': 'admin',
        #         'PASSWORD': os.getenv("DATABASE_PASSWORD"),
        #         # 'HOST': 'localhost',
        #         'HOST': os.getenv("DATABASE_HOST"),
        # >>>>>>> develop
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
