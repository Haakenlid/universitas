# -*- coding: utf-8 -*-
"""
Django settings for universitas_no project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: path.join(SITE_ROOT, ...)
from os import environ
from os.path import abspath, dirname, join, normpath
import django.conf.global_settings as DEFAULT_SETTINGS

# PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
BASE_DIR = environ["DJANGO_SOURCE_FOLDER"]

# Absolute filesystem path to the top-level project folder:
PROJECT_ROOT_FOLDER = dirname(BASE_DIR)
# These values are set in the virtualenv postactivate bash file

SECRET_KEY = environ["DJANGO_SECRET_KEY"]
SITE_URL = environ["DJANGO_SITE_URL"]

# Prodsys for universitas.
PRODSYS_USER = environ["DJANGO_PRODSYS_USER"]
PRODSYS_PASSWORD = environ["DJANGO_PRODSYS_PASSWORD"]
PRODSYS_URL = environ["DJANGO_PRODSYS_URL"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# CUSTOM APPS
INSTALLED_APPS = (
    'myapps.issues',
    'myapps.stories',
    'myapps.core',
    'myapps.photo',
    'myapps.frontpage',
    'myapps.contributors',
    'myapps.markup',
    'myapps.legacy_db',
    'myapps.adverts',
    'functional_tests',
    )

# THIRD PARTY APPS
INSTALLED_APPS = (
    # 'django_nose',
    'autocomplete_light',
    'django_extensions',
    'compressor',
    'sekizai',
    'sorl.thumbnail',
    'watson',
    ) + INSTALLED_APPS

# CORE APPS
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    ) + INSTALLED_APPS


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'universitas_no.urls'
WSGI_APPLICATION = 'universitas_no.wsgi.application'



LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/'
LOGIN_URL = '/admin/login/'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': environ["DJANGO_DB_NAME"],
        'USER': environ["DJANGO_DB_USER"],
        'PASSWORD': environ["DJANGO_DB_PASSWORD"],
        'HOST': 'localhost',
        'PORT': '5432',       # Set to empty string for default.
    },
    'prodsys': {
        'ENGINE': 'mysql.connector.django',
        'NAME': environ["DJANGO_PRODSYS_DB_NAME"],
        'USER': environ["DJANGO_PRODSYS_DB_USER"],
        'PASSWORD': environ["DJANGO_PRODSYS_DB_PASSWORD"],
        # 'HOST': environ["DJANGO_PRODSYS_DB_HOST"],
        'HOST': 'localhost', # TODO: Endre dette tilbake det er bare et eksperiment.
        'PORT': '',       # Set to empty string for default.
    }
}
DATABASE_ROUTERS = ['myapps.legacy_db.router.ProdsysRouter']

#SORL
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
THUMBNAIL_ENGINE = 'myapps.photo.thumbnail_engine.CloseCropEngine'
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o6770
FILE_UPLOAD_PERMISSIONS = 0o664

# CACHE
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 0,
            # 'PASSWORD': 'yadayada',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            }
        },
    },
}


# # When using unix domain sockets with Redis
# # Note: ``LOCATION`` needs to be the same as the ``unixsocket`` setting
# # in your redis.conf
# CACHES = {
#     'default': {
#         'BACKEND': 'redis_cache.RedisCache',
#         'LOCATION': '/path/to/socket/file',
#         'OPTIONS': {
#             'DB': 1,
#             'PASSWORD': 'yadayada',
#             'PARSER_CLASS': 'redis.connection.HiredisParser'
#         },
#     },


# STATIC FILE CONFIGURATION
STATIC_ROOT = normpath(join(PROJECT_ROOT_FOLDER, 'static'))
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    normpath(join(BASE_DIR, 'assets')),
)

# INTERNATIONALIZATION
# LANGUAGE_CODE = 'en'
LANGUAGE_CODE = 'NB_no'
TIME_ZONE = 'Europe/Oslo'
USE_I18N = True  # Internationalisation (string translation)
USE_L10N = True  # Localisation (numbers and stuff)
USE_TZ = True  # Use timezone
LOCALE_PATHS = (
    normpath(join(BASE_DIR, 'translation')),
    )

DATE_FORMAT = 'j. F, Y'
DATETIME_FORMAT = 'Y-m-d H:i'
SHORT_DATE_FORMAT = 'Y-m-d'
SHORT_DATETIME_FORMAT = 'y-m-d H:i'



# MEDIA_ROOT = normpath(join(PHOTO_ARCHIVE, 'upload'))
MEDIA_ROOT = '/srv/fotoarkiv_universitas'
MEDIA_URL = '/foto/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'compressor.finders.CompressorFinder',
)
# END STATIC FILE CONFIGURATION

# TEMPLATES AND FIXTURES CONFIGURATION
FIXTURE_DIRS = (
    normpath(join(BASE_DIR, 'fixtures')),
)
TEMPLATE_DIRS = (
    normpath(join(BASE_DIR, 'templates')),
)
TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'sekizai.context_processors.sekizai',
    'django.core.context_processors.request',
)
# END TEMPLATES AND FIXTURES CONFIGURATION

LOG_FOLDER = normpath(join(PROJECT_ROOT_FOLDER, 'logs'))


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(name)s%(levelname)6s %(filename)25s:%(lineno)-4d (%(funcName)s) - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'minimal': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'stream_to_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename':   normpath(join(LOG_FOLDER, 'django.log')),
            'formatter': 'verbose',
        },
        'bylines_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename':   normpath(join(LOG_FOLDER, 'bylines.log')),
            'formatter': 'minimal',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'stream_to_console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'universitas': {
            'handlers': ['stream_to_console', 'file',],
            'level': 'DEBUG',
            'propagate': False,
        },
        'bylines': {
            'handlers': ['bylines_file',],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}