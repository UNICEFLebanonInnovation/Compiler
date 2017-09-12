# -*- coding: utf-8 -*-
"""
Production Configurations

<<<<<<< HEAD
- Use djangosecure
- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send emails
- Use Redis on Heroku
=======
- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send emails
- Use Redis for cache
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

- Use sentry for error logging


<<<<<<< HEAD
=======
- Use opbeat for error reporting

>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
"""
from __future__ import absolute_import, unicode_literals

from boto.s3.connection import OrdinaryCallingFormat
from django.utils import six

import logging


<<<<<<< HEAD
from .common import *  # noqa
=======
from .base import *  # noqa
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env('DJANGO_SECRET_KEY')

<<<<<<< HEAD
# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# django-secure
# ------------------------------------------------------------------------------
INSTALLED_APPS += ('djangosecure', )
# raven sentry client
# See https://docs.getsentry.com/hosted/clients/python/integrations/django/
INSTALLED_APPS += ('raven.contrib.django.raven_compat', )
SECURITY_MIDDLEWARE = (
    'djangosecure.middleware.SecurityMiddleware',
)
# Use Whitenoise to serve static files
# See: https://whitenoise.readthedocs.io/
WHITENOISE_MIDDLEWARE = (
    'whitenoise.middleware.WhiteNoiseMiddleware',
)
MIDDLEWARE_CLASSES = WHITENOISE_MIDDLEWARE + MIDDLEWARE_CLASSES
RAVEN_MIDDLEWARE = (
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
)
MIDDLEWARE_CLASSES = RAVEN_MIDDLEWARE + MIDDLEWARE_CLASSES

# Make sure djangosecure.middleware.SecurityMiddleware is listed first
MIDDLEWARE_CLASSES = SECURITY_MIDDLEWARE + MIDDLEWARE_CLASSES

=======

# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# raven sentry client
# See https://docs.sentry.io/clients/python/integrations/django/
INSTALLED_APPS += ['raven.contrib.django.raven_compat', ]

# Use Whitenoise to serve static files
# See: https://whitenoise.readthedocs.io/
WHITENOISE_MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ]
MIDDLEWARE = WHITENOISE_MIDDLEWARE + MIDDLEWARE
RAVEN_MIDDLEWARE = ['raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware']
MIDDLEWARE = RAVEN_MIDDLEWARE + MIDDLEWARE
# opbeat integration
# See https://opbeat.com/languages/django/
INSTALLED_APPS += ['opbeat.contrib.django', ]
OPBEAT = {
    'ORGANIZATION_ID': env('DJANGO_OPBEAT_ORGANIZATION_ID'),
    'APP_ID': env('DJANGO_OPBEAT_APP_ID'),
    'SECRET_TOKEN': env('DJANGO_OPBEAT_SECRET_TOKEN')
}
MIDDLEWARE = ['opbeat.contrib.django.middleware.OpbeatAPMMiddleware', ] + MIDDLEWARE


# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

# set this to 60 seconds and then to 518400 when you can prove it works
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    'DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
<<<<<<< HEAD
=======
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
<<<<<<< HEAD
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['compile.uniceflebanon.org'])
# END SITE CONFIGURATION

INSTALLED_APPS += ('gunicorn', )
=======
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS','172.16.1.170', '0.0.0.0', default=['mdb2.uniceflebanon.org', ])
# END SITE CONFIGURATION

INSTALLED_APPS += ['gunicorn', ]

>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

# STORAGE CONFIGURATION
# ------------------------------------------------------------------------------
# Uploaded Media Files
# ------------------------
# See: http://django-storages.readthedocs.io/en/latest/index.html
<<<<<<< HEAD
INSTALLED_APPS += (
    'storages',
)
=======
INSTALLED_APPS += ['storages', ]
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

AWS_ACCESS_KEY_ID = env('DJANGO_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('DJANGO_AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME')
AWS_AUTO_CREATE_BUCKET = True
AWS_QUERYSTRING_AUTH = False
AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()

# AWS cache settings, don't change unless you know what you're doing:
AWS_EXPIRY = 60 * 60 * 24 * 7

# TODO See: https://github.com/jschneier/django-storages/issues/47
# Revert the following and use str after the above-mentioned bug is fixed in
# either django-storage-redux or boto
<<<<<<< HEAD
AWS_HEADERS = {
    'Cache-Control': six.b('max-age=%d, s-maxage=%d, must-revalidate' % (
        AWS_EXPIRY, AWS_EXPIRY))
=======
control = 'max-age=%d, s-maxage=%d, must-revalidate' % (AWS_EXPIRY, AWS_EXPIRY)
AWS_HEADERS = {
    'Cache-Control': control
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
}

# URL that handles the media served from MEDIA_ROOT, used for managing
# stored files.
MEDIA_URL = 'https://s3.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME


# Static Assets
# ------------------------
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

<<<<<<< HEAD
# EMAIL
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL',
                         default='Student Registration <noreply@monitoring.uniceflebanon.org>')
EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY = env('MAILGUN_API_KEY', default='NO_MAILGUN_API_KEY')
MAILGUN_SERVER_NAME = env('MAILGUN_SERVER_NAME', default='NO_MAILGUN_SERVER_NAME')
EMAIL_SUBJECT_PREFIX = env('EMAIL_SUBJECT_PREFIX', default='[Student Registration] ')
SERVER_EMAIL = env('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
NEW_RELIC_LICENSE_KEY = env('NEW_RELIC_LICENSE_KEY', default='NO_RELIC_LICENSE_KEY')
NEW_RELIC_APP_NAME = env('NEW_RELIC_APP_NAME', default='NO_RELIC_APP_NAME')
=======
# COMPRESSOR
# ------------------------------------------------------------------------------
COMPRESS_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
COMPRESS_URL = STATIC_URL
COMPRESS_ENABLED = env.bool('COMPRESS_ENABLED', default=True)
# EMAIL
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL',
                         default='Student Registration <noreply@compiler.uniceflebanon.org>')
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[Student Registration]')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# Anymail with Mailgun
INSTALLED_APPS += ['anymail', ]
ANYMAIL = {
    'MAILGUN_API_KEY': env('DJANGO_MAILGUN_API_KEY'),
    'MAILGUN_SENDER_DOMAIN': env('MAILGUN_SENDER_DOMAIN')
}
EMAIL_BACKEND = 'anymail.backends.mailgun.MailgunBackend'
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
]

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
<<<<<<< HEAD
# Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
DATABASES['default'] = env.db('DATABASE_URL')

# CACHING
# ------------------------------------------------------------------------------
=======

# Use the Heroku-style specification
# Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
DATABASES['default'] = env.db('DATABASE_URL')

if env.bool('DATABASE_SSL_ENABLED', default=False):
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}

# CACHING
# ------------------------------------------------------------------------------

REDIS_LOCATION = '{0}/{1}'.format(env('REDIS_URL', default='redis://127.0.0.1:6379'), 0)
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
# Heroku URL does not pass the DB number, so we parse it in
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
<<<<<<< HEAD
        'LOCATION': '{0}/{1}'.format(env('REDIS_URL', default='redis://127.0.0.1:6379'), 0),
=======
        'LOCATION': REDIS_LOCATION,
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,  # mimics memcache behavior.
                                        # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        }
    }
}


# Sentry Configuration
<<<<<<< HEAD
SENTRY_DSN = env('SENTRY_DSN')
SENTRY_CLIENT = env('SENTRY_CLIENT', default='raven.contrib.django.raven_compat.DjangoClient')
=======
SENTRY_DSN = env('DJANGO_SENTRY_DSN')
SENTRY_CLIENT = env('DJANGO_SENTRY_CLIENT', default='raven.contrib.django.raven_compat.DjangoClient')
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
<<<<<<< HEAD
        'level': 'INFO',
        'handlers': ['sentry', 'console'],
=======
        'level': 'WARNING',
        'handlers': ['sentry', ],
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
<<<<<<< HEAD
            'handlers': ['console'],
=======
            'handlers': ['console', ],
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
<<<<<<< HEAD
            'handlers': ['console'],
=======
            'handlers': ['console', ],
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
<<<<<<< HEAD
            'handlers': ['console'],
=======
            'handlers': ['console', ],
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
<<<<<<< HEAD
            'handlers': ['console', 'sentry'],
=======
            'handlers': ['console', 'sentry', ],
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
            'propagate': False,
        },
    },
}
<<<<<<< HEAD
SENTRY_CELERY_LOGLEVEL = env.int('SENTRY_LOG_LEVEL', logging.INFO)
RAVEN_CONFIG = {
    'CELERY_LOGLEVEL': env.int('SENTRY_LOG_LEVEL', logging.INFO),
=======
SENTRY_CELERY_LOGLEVEL = env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO)
RAVEN_CONFIG = {
    'CELERY_LOGLEVEL': env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO),
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    'DSN': SENTRY_DSN
}

# Custom Admin URL, use {% url 'admin:index' %}
<<<<<<< HEAD
# ADMIN_URL = env('ADMIN_URL')

# Your production stuff: Below this line define 3rd party library settings

DEBUG = env.bool('DJANGO_DEBUG', False)
=======
ADMIN_URL = env('DJANGO_ADMIN_URL')

# Your production stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
