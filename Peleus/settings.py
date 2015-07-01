"""
Django settings for Peleus project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from forecast.settings import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3k5h20ji8$_f^iycfc$1g#s2b%fwd7q2fby@(r8m+9s6^4zr0a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

APPEND_SLASH = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

APP_NAME = "Peleus"


# Application definition

INSTALLED_APPS = (
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'captcha',
    'django_countries',
    'forecast',
    'taggit',
    'django_object_actions',
    'postman'
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'Peleus.urls'

WSGI_APPLICATION = 'Peleus.wsgi.application'

LOGIN_REDIRECT_URL = '/'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    # 'default': {
    # 'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'peleus',
    #     'USER': 'peleus',
    #     'PASSWORD': 'WeakPassw0rd!',
    #     'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
    #     'PORT': '3306',
    # }
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': ("django.contrib.auth.context_processors.auth",
                                           "django.core.context_processors.request",
                                           "forecast.context_processors.forecast_user",
                                           "forecast.context_processors.forecast_stuff",
                                           # "forecast.context_processors.forecast_filters",
                                           "django.template.context_processors.debug",
                                           "django.template.context_processors.i18n",
                                           "django.template.context_processors.media",
                                           "django.template.context_processors.static",
                                           "django.template.context_processors.tz",
                                           "django.contrib.messages.context_processors.messages")},
        'DIRS': (os.path.join(BASE_DIR, 'templates'),)
    },
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'forecast', 'static', 'media')
MEDIA_URL = '/media/'

RECAPTCHA_PUBLIC_KEY = '6Ldr5gYTAAAAAOWBFg4rtP6UKZs54wqC1Xa7t4UR'
RECAPTCHA_PRIVATE_KEY = '6Ldr5gYTAAAAAMfzv_K8zfPcdzSi1YSU2_PbvZH5'
NOCAPTCHA = True
RECAPTCHA_USE_SSL = True

TOKEN_EXPIRATION_PERIOD = 5  # set in hours
TOKEN_LENGTH = 64


# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025

EMAIL_HOST = 'smtp.gmail.com'

# EMAIL_HOST_USER = 'Peleus.key@gmail.com'
EMAIL_HOST_USER = 'peleus.noreply@gmail.com'
# EMAIL_HOST_PASSWORD = 'Castle12!21'
EMAIL_HOST_PASSWORD = 'laserunicorns'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# DEFAULT_EMAIL = 'no-reply@peleus.com'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USER = 'Peleus.key@gmail.com'
# EMAIL_PASSWORD = 'Castle12!21'
_EMAIL_TEMPLATE_FILE = 'email.html'
EMAIL_TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates', 'email', _EMAIL_TEMPLATE_FILE)
MAIL_USE_TLS = True

DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'

DOMAIN_NAME = 'http://213.174.22.120:8088'   # change this in production

AUTH_PROFILE_MODULE = 'forecast.CustomUserProfile'