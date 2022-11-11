"""
Django settings for creator_coin_new project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from dotenv import load_dotenv


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv( os.path.join(env_dir, '.env') )


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if 'SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['SECRET_KEY']
else:
    SECRET_KEY = 'xel#f$gd8wtjy)zu6(#=liq1y(0nu*57yh4#kh^ddi(x8ildih'


# SECURITY WARNING: don't run with debug turned on in production!
if 'RDS_DB_NAME' in os.environ:
    DEBUG = False
else:
    DEBUG = True


ALLOWED_HOSTS = ['127.0.0.1', 'creatorcoin.app', 'www.creatorcoin.app']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'creator_coin',

    'storages',
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

ROOT_URLCONF = 'creator_coin_new.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'creator_coin_new.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
         'rest_framework.renderers.JSONRenderer',
     )
}


if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'creator_coin_db',
            'USER': 'rahul_creator_coin',
            'PASSWORD': os.getenv("test_db_password"),
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
 

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

AUTH_USER_MODEL = 'creator_coin.Web3User'

# STATIC_URL = '/static/'

STATIC_URL = '/static/'
if 'RDS_DB_NAME' in os.environ:
    STATIC_ROOT = 'static'
else:
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'static'),
    )


# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# for auto-created primary keys
DEFAULT_AUTO_FIELD='django.db.models.AutoField' 

if 'RDS_DB_NAME' in os.environ:
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
else:
    AWS_STORAGE_BUCKET_NAME = os.getenv("aws_storage_bucket_name")
    AWS_S3_REGION_NAME = os.getenv("aws_s3_region_name")
    AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
    AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")

# Tell django-storages the domain to use to refer to static files.
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# # Tell the staticfiles app to use S3Boto3 storage when writing the collected static files (when
# # you run `collectstatic`).
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'custom_storages.StaticStorage'

MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'

if 'RDS_DB_NAME' in os.environ:

    LOGGING = {
        'version': 1,
        # The version number of our log
        'disable_existing_loggers': False,
        # django uses some of its own loggers for internal operations. In case you want to disable them just replace the False above with true.
        # A handler for WARNING. It is basically writing the WARNING messages into a file called WARNING.log
        "formatters": {
            "verbose": {"format": "%(asctime)s %(levelname)s %(module)s: %(message)s"}
        },
        'handlers': {
            'file': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                "filename": "/var/app/current/analyzer.log",
                "formatter": "verbose",
            },
        },
        # A logger for WARNING which has a handler called 'file'. A logger can have multiple handler
        'loggers': {
            # notice the blank '', Usually you would put built in loggers like django or root here based on your needs
            '': {
                'handlers': ['file'], #notice how file variable is called in handler which has been defined above
                'level': 'WARNING',
                'propagate': True,
            },
        },
    }

else:
    
    LOGGING = {
        'version': 1,
        # The version number of our log
        'disable_existing_loggers': False,
        # django uses some of its own loggers for internal operations. In case you want to disable them just replace the False above with true.
        # A handler for WARNING. It is basically writing the WARNING messages into a file called WARNING.log
        "formatters": {
            "verbose": {"format": "%(asctime)s %(levelname)s %(module)s: %(message)s"}
        },
        'handlers': {
            'file': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'warning.log'),
                "formatter": "verbose",
            },
        },
        # A logger for WARNING which has a handler called 'file'. A logger can have multiple handler
        'loggers': {
            # notice the blank '', Usually you would put built in loggers like django or root here based on your needs
            '': {
                'handlers': ['file'], #notice how file variable is called in handler which has been defined above
                'level': 'WARNING',
                'propagate': True,
            },
        },
    }



if 'RDS_DB_NAME' in os.environ:
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    X_FRAME_OPTIONS = 'DENY'
    



